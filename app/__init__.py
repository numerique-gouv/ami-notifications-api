from pathlib import Path
from typing import Any, Callable

import sentry_sdk
from litestar import (
    Litestar,
    Response,
    get,
)
from litestar.channels import ChannelsPlugin
from litestar.channels.backends.memory import MemoryChannelsBackend
from litestar.config.cors import CORSConfig
from litestar.contrib.jinja import JinjaTemplateEngine
from litestar.di import Provide
from litestar.static_files import (
    create_static_files_router,  # type: ignore[reportUnknownVariableType]
)
from litestar.stores.file import FileStore
from litestar.template.config import TemplateConfig
from webpush import WebPush

from app import env
from app.controllers.auth import AuthController
from app.controllers.notification import NotificationController
from app.controllers.registration import RegistrationController
from app.controllers.user import UserController
from app.database import alchemy

from .admin.routes import router as ami_admin_router
from .data.routes import data_router
from .rvo.routes import router as rvo_router

cors_config = CORSConfig(allow_origins=["*"])


sentry_sdk.init(
    dsn=env.SENTRY_DSN,
    environment=env.SENTRY_ENV,
    # Add data like request headers and IP for users, if applicable;
    # see https://docs.sentry.io/platforms/python/data-management/data-collected/ for more info
    # send_default_pii=True,
)

# ### VIEWS


@get(path="/sector_identifier_url", include_in_schema=False)
async def get_sector_identifier_url() -> Response[Any]:
    redirect_uris: list[str] = [
        url.strip() for url in env.PUBLIC_SECTOR_IDENTIFIER_URL.strip().split("\n")
    ]
    return Response(redirect_uris)


# ### APP


def provide_webpush() -> WebPush:
    webpush = WebPush(
        public_key=env.VAPID_PUBLIC_KEY.encode(),
        private_key=env.VAPID_PRIVATE_KEY.encode(),
        subscriber="contact.ami@numerique.gouv.fr",
    )
    return webpush


def create_app(
    webpush_init: Callable[[], WebPush] = provide_webpush,
) -> Litestar:
    return Litestar(
        route_handlers=[
            AuthController,
            RegistrationController,
            NotificationController,
            UserController,
            data_router,
            get_sector_identifier_url,
            create_static_files_router(
                path="/",
                directories=[env.HTML_DIR],
                html_mode=True,
            ),
            rvo_router,
            ami_admin_router,
        ],
        dependencies={
            "webpush": Provide(webpush_init, use_cache=True, sync_to_thread=True),
        },
        plugins=[
            alchemy,
            ChannelsPlugin(
                channels=["notification_events"], backend=MemoryChannelsBackend(history=0)
            ),
        ],
        template_config=TemplateConfig(directory=Path("templates"), engine=JinjaTemplateEngine),
        cors_config=cors_config,
        stores={"sessions": FileStore(path=Path("session_data"))},
    )
