import json
import os
from contextlib import AbstractAsyncContextManager
from pathlib import Path
from typing import Annotated, Any, Callable, cast

import httpx
import sentry_sdk
from litestar import (
    Litestar,
    Request,
    Response,
    get,
    patch,
    post,
)
from litestar.config.cors import CORSConfig
from litestar.contrib.jinja import JinjaTemplateEngine
from litestar.di import Provide
from litestar.exceptions import NotFoundException
from litestar.middleware.session.server_side import ServerSideSessionConfig
from litestar.params import Body
from litestar.response import Template
from litestar.response.redirect import Redirect
from litestar.static_files import (
    create_static_files_router,  # type: ignore[reportUnknownVariableType]
)
from litestar.status_codes import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_500_INTERNAL_SERVER_ERROR,
)
from litestar.stores.file import FileStore
from litestar.template.config import TemplateConfig
from sqlalchemy.orm import InstrumentedAttribute, selectinload
from sqlmodel.ext.asyncio.session import AsyncSession
from webpush import WebPush, WebPushSubscription

from .database import db_connection, provide_db_session
from .models import (
    Notification,
    Registration,
    RegistrationCreation,
    RegistrationEnable,
    RegistrationRename,
    User,
    create_notification,
    create_registration,
    create_user,
    get_notification_list,
    get_registration_by_id,
    get_registration_by_user_and_subscription,
    get_user_by_email,
    get_user_by_id,
    get_user_list,
    update_registration,
)
from .rvo import rvo_router

cors_config = CORSConfig(allow_origins=["*"])
session_config = ServerSideSessionConfig()


sentry_sdk.init(
    dsn=os.getenv("SENTRY_DSN", ""),
    environment=os.getenv("SENTRY_ENV", ""),
    # Add data like request headers and IP for users, if applicable;
    # see https://docs.sentry.io/platforms/python/data-management/data-collected/ for more info
    # send_default_pii=True,
)

# This is the folder where the svelte PWA is built statically.
HTML_DIR = "public/mobile-app/build"

# This is the folder where the "admin" (test API client) is.
HTML_DIR_ADMIN = "public"

PUBLIC_FC_AMI_CLIENT_ID = os.getenv("PUBLIC_FC_AMI_CLIENT_ID", "")
FC_AMI_CLIENT_SECRET = os.getenv("FC_AMI_CLIENT_SECRET", "")
PUBLIC_FC_BASE_URL = os.getenv("PUBLIC_FC_BASE_URL", "")
PUBLIC_FC_AMI_REDIRECT_URL = os.getenv("PUBLIC_FC_AMI_REDIRECT_URL", "")
PUBLIC_FC_TOKEN_ENDPOINT = os.getenv("PUBLIC_FC_TOKEN_ENDPOINT", "")
PUBLIC_FC_JWKS_ENDPOINT = os.getenv("PUBLIC_FC_JWKS_ENDPOINT", "")
PUBLIC_FC_USERINFO_ENDPOINT = os.getenv("PUBLIC_FC_USERINFO_ENDPOINT", "")
PUBLIC_FC_LOGOUT_ENDPOINT = os.getenv("PUBLIC_FC_LOGOUT_ENDPOINT", "")
PUBLIC_API_URL = os.getenv("PUBLIC_API_URL", "")
PUBLIC_APP_URL = os.getenv("PUBLIC_APP_URL", "")

#### ENDPOINTS


@get("/notification-key")
async def get_notification_key() -> str:
    return os.getenv("VAPID_APPLICATION_SERVER_KEY", "")


@post("/api/v1/registrations")
async def register(
    db_session: AsyncSession,
    data: Annotated[
        RegistrationCreation,
        Body(
            title="Register to receive notifications",
            description="Register with a push subscription and an email to receive notifications",
        ),
    ],
) -> Response[Registration]:
    WebPushSubscription.model_validate(data.subscription)
    try:
        user = await get_user_by_email(data.email, db_session)
    except NotFoundException:
        user = await create_user(data.email, db_session)

    assert user.id is not None, "User ID should be set after commit"
    existing_registration = await get_registration_by_user_and_subscription(
        data.subscription, db_session, user
    )
    if existing_registration:
        # This registration already exists, don't duplicate it.
        return Response(existing_registration, status_code=HTTP_200_OK)

    registration = await create_registration(
        data.subscription, data.label, data.enabled, db_session, user.id
    )
    return Response(registration, status_code=HTTP_201_CREATED)


@post("/api/v1/notifications")
async def notify(
    db_session: AsyncSession,
    webpush: WebPush,
    data: Annotated[
        Notification,
        Body(
            title="Send a notification",
            description="Send the notification message to a registered user",
        ),
    ],
) -> Response[Notification]:
    user = await get_user_by_id(
        data.user_id,
        db_session,
        options=selectinload(cast(InstrumentedAttribute[Any], User.registrations)),
    )

    for registration in user.registrations:
        subscription = WebPushSubscription.model_validate(registration.subscription)
        json_data = {"title": data.title, "message": data.message, "sender": data.sender}
        message = webpush.get(message=json.dumps(json_data), subscription=subscription)
        headers = cast(dict[str, str], message.headers)

        response = httpx.post(
            registration.subscription["endpoint"], content=message.encrypted, headers=headers
        )
        response.raise_for_status()
    notification = await create_notification(data, db_session)
    return Response(notification, status_code=HTTP_201_CREATED)


@get("/api/v1/users")
async def list_users(db_session: AsyncSession) -> Response[list[User]]:
    users = await get_user_list(db_session)
    return Response(users, status_code=HTTP_200_OK)


@get("/api/v1/users/{user_id:int}/notifications")
async def get_notifications(db_session: AsyncSession, user_id: int) -> Response[list[Notification]]:
    user: User = await get_user_by_id(
        user_id,
        db_session,
        options=selectinload(cast(InstrumentedAttribute[Any], User.notifications)),
    )
    return Response(user.notifications, status_code=HTTP_200_OK)


@get("/api/v1/users/{user_id:int}/registrations")
async def list_registrations(
    db_session: AsyncSession, user_id: int
) -> Response[list[Registration]]:
    user: User = await get_user_by_id(
        user_id,
        db_session,
        options=selectinload(cast(InstrumentedAttribute[Any], User.registrations)),
    )
    return Response(user.registrations, status_code=HTTP_200_OK)


@patch("/api/v1/registrations/{pk:int}/label")
async def rename_registration(
    db_session: AsyncSession,
    pk: int,
    data: Annotated[RegistrationRename, Body(description="New label for the registration")],
) -> Response[Registration]:
    registration = await get_registration_by_id(db_session, pk)
    registration.label = data.label
    registration = await update_registration(db_session, registration)
    return Response(registration, status_code=HTTP_200_OK)


@patch("/api/v1/registrations/{pk:int}/enabled")
async def enable_registration(
    db_session: AsyncSession,
    pk: int,
    data: Annotated[RegistrationEnable, Body(description="Enable or disable the registration")],
) -> Response[Registration]:
    registration = await get_registration_by_id(db_session, pk)
    registration.enabled = data.enabled
    registration = await update_registration(db_session, registration)
    return Response(registration, status_code=HTTP_200_OK)


@get(path="/api/v1/userinfo")
async def get_userinfo(
    request: Request[Any, Any, Any],
) -> Response[Any]:
    """This endpoint "forwards" the request coming from the frontend (the app).

    The app doesn't seem to be allowed to query FranceConnect servers directly, so this endpoint is acting as a proxy.

    """
    access_token = request.headers["authorization"].replace("Bearer ", "")
    userinfo_endpoint_headers = f"Bearer {access_token}"
    response = httpx.get(
        f"{PUBLIC_FC_BASE_URL}{PUBLIC_FC_USERINFO_ENDPOINT}",
        headers={"authorization": userinfo_endpoint_headers},
    )
    return Response(response.json(), status_code=response.status_code)


#### VIEWS


@get(path="/admin/", include_in_schema=False)
async def admin(db_session: AsyncSession) -> Template:
    users = await get_user_list(db_session)
    notifications = await get_notification_list(db_session)
    return Template(
        template_name="admin.html",
        context={"users": users, "notifications": notifications},
    )


@get(path="/login-callback", include_in_schema=False)
async def login_callback(
    code: str,
) -> Response[Any]:
    # FC - Step 5
    redirect_uri: str = f"{PUBLIC_FC_AMI_REDIRECT_URL}"
    client_id: str = PUBLIC_FC_AMI_CLIENT_ID
    client_secret: str = FC_AMI_CLIENT_SECRET
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
        f"{PUBLIC_FC_BASE_URL}{PUBLIC_FC_TOKEN_ENDPOINT}",
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

    return Redirect(f"{PUBLIC_APP_URL}/", query_params=params)


@get(path="/logout", include_in_schema=False)
async def logout(request: Request[Any, Any, Any]) -> Response[Any]:
    if "userinfo" not in request.session or "id_token" not in request.session:
        return Redirect("/")

    logout_url: str = f"{PUBLIC_FC_BASE_URL}{PUBLIC_FC_LOGOUT_ENDPOINT}"
    data: dict[str, str] = {
        "id_token_hint": request.session.get("id_token", ""),
        "state": "not-implemented-yet-and-has-more-than-32-chars",
        "post_logout_redirect_uri": f"{PUBLIC_API_URL}/logout-callback",
    }

    # Redirect the user to FC's logout service. The local session cleanup happens in `/logout-callback`.
    return Redirect(logout_url, query_params=data)


@get(path="/logout-callback", include_in_schema=False)
async def logout_callback(request: Request[Any, Any, Any]) -> Response[Any]:
    # Local session cleanup: the user was logged out from FC.
    del request.session["userinfo"]
    del request.session["id_token"]
    return Redirect(f"{PUBLIC_APP_URL}/#/logged_out")


def error_from_response(response: Response[str], ami_details: str | None = None) -> Response[str]:
    details = response.json()  # type: ignore[reportUnknownVariableType]
    if ami_details is not None:
        details["ami_details"] = ami_details
    return Response(details, status_code=response.status_code)  # type: ignore[reportUnknownVariableType]


def error_from_message(
    message: dict[str, str], status_code: int | None
) -> Response[dict[str, str]]:
    return Response(message, status_code=status_code)


#### APP


def provide_webpush() -> WebPush:
    webpush = WebPush(
        public_key=os.getenv("VAPID_PUBLIC_KEY", "").encode(),
        private_key=os.getenv("VAPID_PRIVATE_KEY", "").encode(),
        subscriber="contact.ami@numerique.gouv.fr",
    )
    return webpush


def create_app(
    database_connection: Callable[[Litestar], AbstractAsyncContextManager[None]] = db_connection,
    webpush_init: Callable[[], WebPush] = provide_webpush,
) -> Litestar:
    return Litestar(
        route_handlers=[
            get_notification_key,
            register,
            notify,
            list_users,
            list_registrations,
            rename_registration,
            enable_registration,
            get_notifications,
            admin,
            login_callback,
            get_userinfo,
            logout,
            logout_callback,
            create_static_files_router(
                path="/admin/static",
                directories=[HTML_DIR_ADMIN],
                html_mode=True,
            ),
            create_static_files_router(
                path="/",
                directories=[HTML_DIR],
                html_mode=True,
            ),
            rvo_router,
        ],
        dependencies={
            "db_session": Provide(provide_db_session),
            "webpush": Provide(webpush_init, use_cache=True, sync_to_thread=True),
        },
        lifespan=[database_connection],
        template_config=TemplateConfig(directory=Path("templates"), engine=JinjaTemplateEngine),
        cors_config=cors_config,
        middleware=[session_config.middleware],
        stores={"sessions": FileStore(path=Path("session_data"))},
    )
