from pathlib import Path

import firebase_admin
import sentry_sdk
from litestar import (
    Litestar,
    Router,
)
from litestar.channels import ChannelsPlugin
from litestar.channels.backends.asyncpg import AsyncPgChannelsBackend
from litestar.config.cors import CORSConfig
from litestar.contrib.jinja import JinjaTemplateEngine
from litestar.di import Provide
from litestar.static_files import (
    create_static_files_router,  # type: ignore[reportUnknownVariableType]
)
from litestar.stores.file import FileStore
from litestar.template.config import TemplateConfig
from sentry_sdk.integrations.litestar import LitestarIntegration

from app import env, errors
from app.auth import jwt_cookie_auth, openapi_config, partner_auth
from app.controllers.auth import AuthController
from app.controllers.notification import (
    NotAuthenticatedNotificationController,
    NotificationController,
    PartnerNotificationController,
)
from app.controllers.partner import NotAuthenticatedPartnerController, PartnerController
from app.controllers.registration import RegistrationController
from app.controllers.scheduled_notification import ScheduledNotificationController
from app.database import alchemy, channels_dsn
from app.httpx import (
    close_httpx_async_client,
    get_httpx_async_client,
    httpx_async_client_provider,
)
from app.webpush import provide_webpush

from .admin.routes import router as ami_admin_router
from .data.routes import data_router
from .rvo.routes import router as rvo_router

cors_config = CORSConfig(allow_origins=[env.PUBLIC_APP_URL], allow_credentials=True)
firebase_app: firebase_admin.App = firebase_admin.initialize_app()  # type: ignore[reportUnknownMemberType]


sentry_sdk.init(
    dsn=env.SENTRY_DSN,
    environment=env.SENTRY_ENV,
    # Add data like request headers and IP for users, if applicable;
    # see https://docs.sentry.io/platforms/python/data-management/data-collected/ for more info
    # send_default_pii=True,
    integrations=[
        LitestarIntegration(
            failed_request_status_codes={s for s in range(400, 599) if s != 401},
        ),
    ],
)

# ### APP


authenticated_router: Router = Router(
    path="/",
    route_handlers=[
        AuthController,
        RegistrationController,
        NotificationController,
        PartnerController,
        ScheduledNotificationController,
        data_router,
    ],
    middleware=[jwt_cookie_auth.middleware],
)

partner_router: Router = Router(
    path="/",
    route_handlers=[PartnerNotificationController],
    middleware=[partner_auth.middleware],
)


def create_app() -> Litestar:
    return Litestar(
        route_handlers=[
            authenticated_router,
            partner_router,
            NotAuthenticatedNotificationController,
            NotAuthenticatedPartnerController,
            create_static_files_router(
                path="/",
                directories=[env.HTML_DIR],
                html_mode=True,
            ),
            rvo_router,
            ami_admin_router,
        ],
        exception_handlers={errors.TechnicalError: errors.technical_error_handler},
        dependencies={
            "webpush": Provide(provide_webpush, use_cache=True, sync_to_thread=True),
            "httpx_async_client": Provide(httpx_async_client_provider),
        },
        plugins=[
            alchemy,
            ChannelsPlugin(
                channels=["notification_events"], backend=AsyncPgChannelsBackend(dsn=channels_dsn)
            ),
        ],
        template_config=TemplateConfig(directory=Path("templates"), engine=JinjaTemplateEngine),
        cors_config=cors_config,
        stores={"sessions": FileStore(path=Path("session_data"))},
        openapi_config=openapi_config,
        on_startup=[get_httpx_async_client],
        on_shutdown=[close_httpx_async_client],
    )
