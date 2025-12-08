from pathlib import Path
from typing import Any, Callable

import sentry_sdk
from litestar import (
    Litestar,
    Response,
    Router,
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
from app.auth import jwt_cookie_auth, openapi_config, partner_auth
from app.controllers.auth import AuthController
from app.controllers.notification import (
    NotAuthenticatedNotificationController,
    NotificationController,
    PartnerNotificationController,
)
from app.controllers.registration import RegistrationController
from app.controllers.user import UserController
from app.database import alchemy
from app.httpx import httpxClient
from app.utils import ami_hash

from .admin.routes import router as ami_admin_router
from .data.routes import data_router
from .rvo.routes import router as rvo_router

cors_config = CORSConfig(allow_origins=[env.PUBLIC_APP_URL], allow_credentials=True)


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


# ### DEV ENDPOINTS


@get(path="/dev-utils/recipient-fc-hash")
async def _dev_utils_recipient_fc_hash(
    given_name: str,
    family_name: str,
    birthdate: str,
    gender: str,
    birthplace: str,
    birthcountry: str,
) -> str:
    hashed_pivot_data: str = ami_hash(
        given_name,
        family_name,
        birthdate,
        gender,
        birthplace,
        birthcountry,
    )
    return hashed_pivot_data


@get(path="/dev-utils/review-apps")
async def _dev_utils_review_apps() -> list[dict[str, str]]:
    """Returns a list of tuples: (review app url, pull request title)."""
    response = httpxClient.get(
        "https://api.github.com/repos/numerique-gouv/ami-notifications-api/pulls",
        params={"state": "open", "sort": "created", "per_page": 100},
        headers={
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    json_data = response.json()
    return [
        {
            "url": f"https://ami-back-staging-pr{review_app['number']}.osc-fr1.scalingo.io/",
            "title": f"PR{review_app['number']}: {review_app['title']}",
            "number": review_app["number"],
            "description": review_app["body"],
        }
        for review_app in json_data
    ]


# ### APP


def provide_webpush() -> WebPush:
    webpush = WebPush(
        public_key=env.VAPID_PUBLIC_KEY.encode(),
        private_key=env.VAPID_PRIVATE_KEY.encode(),
        subscriber="contact.ami@numerique.gouv.fr",
    )
    return webpush


authenticated_router: Router = Router(
    path="/",
    route_handlers=[
        AuthController,
        RegistrationController,
        NotificationController,
        data_router,
    ],
    middleware=[jwt_cookie_auth.middleware],
)

partner_router: Router = Router(
    path="/",
    route_handlers=[PartnerNotificationController],
    middleware=[partner_auth.middleware],
)


def create_app(
    webpush_init: Callable[[], WebPush] = provide_webpush,
) -> Litestar:
    return Litestar(
        route_handlers=[
            authenticated_router,
            partner_router,
            NotAuthenticatedNotificationController,
            UserController,
            get_sector_identifier_url,
            _dev_utils_recipient_fc_hash,
            _dev_utils_review_apps,
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
        openapi_config=openapi_config,
    )
