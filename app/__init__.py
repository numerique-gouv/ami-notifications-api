from pathlib import Path
from typing import Any, Callable

import httpx
import sentry_sdk
from litestar import (
    Litestar,
    Request,
    Response,
    get,
)
from litestar.channels import ChannelsPlugin
from litestar.channels.backends.memory import MemoryChannelsBackend
from litestar.config.cors import CORSConfig
from litestar.contrib.jinja import JinjaTemplateEngine
from litestar.di import Provide
from litestar.middleware.session.server_side import ServerSideSessionConfig
from litestar.response.redirect import Redirect
from litestar.static_files import (
    create_static_files_router,  # type: ignore[reportUnknownVariableType]
)
from litestar.status_codes import (
    HTTP_500_INTERNAL_SERVER_ERROR,
)
from litestar.stores.file import FileStore
from litestar.template.config import TemplateConfig
from webpush import WebPush

from app import env
from app.controllers.notification import NotificationController
from app.controllers.registration import RegistrationController
from app.controllers.user import UserController
from app.database import alchemy

from .ami_admin import ami_admin_router
from .rvo import rvo_router

cors_config = CORSConfig(allow_origins=["*"])
session_config = ServerSideSessionConfig()


sentry_sdk.init(
    dsn=env.SENTRY_DSN,
    environment=env.SENTRY_ENV,
    # Add data like request headers and IP for users, if applicable;
    # see https://docs.sentry.io/platforms/python/data-management/data-collected/ for more info
    # send_default_pii=True,
)

# ### VIEWS


@get(path="/login-callback", include_in_schema=False)
async def login_callback(
    code: str,
) -> Response[Any]:
    # FC - Step 5
    redirect_uri: str = env.PUBLIC_FC_PROXY or env.PUBLIC_FC_AMI_REDIRECT_URL
    client_id: str = env.PUBLIC_FC_AMI_CLIENT_ID
    client_secret: str = env.FC_AMI_CLIENT_SECRET
    data: dict[str, str] = {
        "grant_type": "authorization_code",
        "redirect_uri": redirect_uri,
        "client_id": client_id,
        "client_secret": client_secret,
        "code": code,
    }

    if client_secret == "":
        return error_from_message(
            {"error": "Client secret not provided in .env.local file"},
            HTTP_500_INTERNAL_SERVER_ERROR,
        )

    # FC - Step 6
    token_endpoint_headers: dict[str, str] = {"Content-Type": "application/x-www-form-urlencoded"}
    response: Any = httpx.post(
        f"{env.PUBLIC_FC_BASE_URL}{env.PUBLIC_FC_TOKEN_ENDPOINT}",
        headers=token_endpoint_headers,
        data=data,
    )
    if response.status_code != 200:
        return error_from_response(response, ami_details="FC - Step 6 with " + str(data))
    response_token_data: dict[str, str] = response.json()
    params: dict[str, str] = {
        **response_token_data,
        "is_logged_in": "true",
    }

    return Redirect(f"{env.PUBLIC_APP_URL}/", query_params=params)


@get(path="/api-particulier/quotient", include_in_schema=False)
async def get_api_particulier_quotient(
    request: Request[Any, Any, Any],
) -> Response[Any]:
    """This endpoint "forwards" the request coming from the frontend (the app).

    API Particulier doesn't implement CORS, so the app can't directly query it.
    We thus have this endpoint to act as some kind of proxy.

    """
    response = httpx.get(
        f"{env.PUBLIC_API_PARTICULIER_BASE_URL}{env.PUBLIC_API_PARTICULIER_QUOTIENT_ENDPOINT}?recipient={env.PUBLIC_API_PARTICULIER_RECIPIENT_ID}",
        headers={"authorization": request.headers["authorization"]},
    )
    return Response(response.content, status_code=response.status_code)


@get(path="/sector_identifier_url", include_in_schema=False)
async def get_sector_identifier_url() -> Response[Any]:
    redirect_uris: list[str] = [
        url.strip() for url in env.PUBLIC_SECTOR_IDENTIFIER_URL.strip().split("\n")
    ]
    return Response(redirect_uris)


def error_from_response(response: Response[str], ami_details: str | None = None) -> Response[str]:
    details = response.json()  # type: ignore[reportUnknownVariableType]
    if ami_details is not None:
        details["ami_details"] = ami_details
    return Response(details, status_code=response.status_code)  # type: ignore[reportUnknownVariableType]


def error_from_message(
    message: dict[str, str], status_code: int | None
) -> Response[dict[str, str]]:
    return Response(message, status_code=status_code)


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
            RegistrationController,
            NotificationController,
            UserController,
            login_callback,
            get_api_particulier_quotient,
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
        middleware=[session_config.middleware],
        stores={"sessions": FileStore(path=Path("session_data"))},
    )
