import json
import os
from contextlib import AbstractAsyncContextManager
from pathlib import Path
from typing import Annotated, Any, Callable, cast

import httpx
import jwt
import sentry_sdk
from litestar import (
    Litestar,
    Request,  # type: ignore[reportUnknownVariableType]
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
from litestar.status_codes import HTTP_200_OK, HTTP_201_CREATED
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

cors_config = CORSConfig(allow_origins=["*"])


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

TEST_FS_CLIENT_ID = os.getenv("TEST_FS_CLIENT_ID", "")
TEST_FS_CLIENT_SECRET = os.getenv("TEST_FS_CLIENT_SECRET", "")


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


#### VIEWS


@get(path="/admin/", include_in_schema=False)
async def admin(db_session: AsyncSession) -> Template:
    users = await get_user_list(db_session)
    notifications = await get_notification_list(db_session)
    return Template(
        template_name="admin.html",
        context={"users": users, "notifications": notifications},
    )


@get(path="/ami-fs-test-login", include_in_schema=False)
async def ami_fs_test_login() -> Template:
    print(cors_config)
    return Template(
        template_name="ami-fs-test-login.html",
        context={},
    )


@get(path="/ami-fs-test-login-callback", include_in_schema=False)
async def ami_fs_test_login_callback(
    code: str,
    request: Request,  # type: ignore
) -> Response[Any]:
    # FC - Step 5
    FC_URL = "https://fcp-low.sbx.dev-franceconnect.fr"
    TOKEN_FC_PATH = "/api/v2/token"
    JWKS_FC_PATH = "/api/v2/jwks"
    USERINFO_FC_PATH = "/api/v2/userinfo"
    token_endpoint_headers = {"Content-Type": "application/x-www-form-urlencoded"}
    FS_URL = "https://localhost:8000"
    DATA_CALLBACK_FS_PATH = "/ami-fs-test-login-callback"
    redirect_uri = f"{FS_URL}{DATA_CALLBACK_FS_PATH}"
    client_id = TEST_FS_CLIENT_ID
    client_secret = TEST_FS_CLIENT_SECRET
    data = {
        "grant_type": "authorization_code",
        "redirect_uri": redirect_uri,
        "client_id": client_id,
        "client_secret": client_secret,
        "code": code,
    }

    # FC - Step 6
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{FC_URL}{TOKEN_FC_PATH}", headers=token_endpoint_headers, data=data
        )
        response_token_data = response.json()

    # FC - Step 8
    async with httpx.AsyncClient() as client:
        await client.get(f"{FC_URL}{JWKS_FC_PATH}")

    # FC - Step 11
    access_token = response_token_data["access_token"]
    userinfo_endpoint_headers = {"Authorization": f"Bearer {access_token}"}
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{FC_URL}{USERINFO_FC_PATH}", headers=userinfo_endpoint_headers
        )
        userinfo_jws = response.text
        userinfo = jwt.decode(
            userinfo_jws, options={"verify_signature": False}, algorithms=["ES256"]
        )

    # FC - Step 16.1
    request.session["userinfo"] = userinfo
    return Redirect("/ami-fs-test-connected")


@get(path="/ami-fs-test-connected", include_in_schema=False)
async def ami_fs_test_connected(
    request: Request,  # type: ignore
) -> Template:
    # FC - Step 16.2
    userinfo = request.session["userinfo"]
    return Template(
        template_name="ami-fs-test-connected.html",
        context={"userinfo": userinfo},
    )


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
            ami_fs_test_login,
            ami_fs_test_login_callback,
            ami_fs_test_connected,
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
        ],
        dependencies={
            "db_session": Provide(provide_db_session),
            "webpush": Provide(webpush_init, use_cache=True, sync_to_thread=True),
        },
        lifespan=[database_connection],
        template_config=TemplateConfig(directory=Path("templates"), engine=JinjaTemplateEngine),
        cors_config=cors_config,
        middleware=[ServerSideSessionConfig().middleware],
        stores={"sessions": FileStore(path=Path("session_data"))},
    )
