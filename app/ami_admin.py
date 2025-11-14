import os
import uuid
from typing import Annotated, Any

import httpx
import jwt
from litestar import (
    Request,
    Response,
    Router,
    get,
)
from litestar.exceptions import NotFoundException
from litestar.params import Parameter
from litestar.response import Template
from litestar.response.redirect import Redirect
from litestar.static_files import (
    create_static_files_router,  # type: ignore[reportUnknownVariableType]
)
from litestar.status_codes import (
    HTTP_500_INTERNAL_SERVER_ERROR,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app import ami_admin_auth
from app.models import Notification, User
from app.services.notification import NotificationService
from app.services.user import UserService

# This is the folder where the static files for the dsfr are stored.
HTML_DIR = "public/mobile-app/node_modules/@gouvfr"

PUBLIC_PRO_CONNECT_AMI_ADMIN_CLIENT_ID = os.getenv("PUBLIC_PRO_CONNECT_AMI_ADMIN_CLIENT_ID", "")
PRO_CONNECT_AMI_ADMIN_CLIENT_SECRET = os.getenv("PRO_CONNECT_AMI_ADMIN_CLIENT_SECRET", "")
PUBLIC_PRO_CONNECT_BASE_URL = os.getenv("PUBLIC_PRO_CONNECT_BASE_URL", "")
PUBLIC_PRO_CONNECT_AMI_ADMIN_REDIRECT_URL = os.getenv(
    "PUBLIC_PRO_CONNECT_AMI_ADMIN_REDIRECT_URL", ""
)
PUBLIC_PRO_CONNECT_AUTHORIZATION_ENDPOINT = os.getenv(
    "PUBLIC_PRO_CONNECT_AUTHORIZATION_ENDPOINT", ""
)
PUBLIC_PRO_CONNECT_TOKEN_ENDPOINT = os.getenv("PUBLIC_PRO_CONNECT_TOKEN_ENDPOINT", "")
PUBLIC_PRO_CONNECT_JWKS_ENDPOINT = os.getenv("PUBLIC_PRO_CONNECT_JWKS_ENDPOINT", "")
PUBLIC_PRO_CONNECT_USERINFO_ENDPOINT = os.getenv("PUBLIC_PRO_CONNECT_USERINFO_ENDPOINT", "")
PUBLIC_PRO_CONNECT_LOGOUT_ENDPOINT = os.getenv("PUBLIC_PRO_CONNECT_LOGOUT_ENDPOINT", "")
PUBLIC_API_URL = os.getenv("PUBLIC_API_URL", "")


@get(path="/", include_in_schema=False)
async def home(request: Request[Any, Any, Any]) -> Template:
    return Template(
        template_name="ami-admin/base.html",
        context={
            "isProConnected": "userinfo" in request.session and "id_token" in request.session,
            "PUBLIC_PRO_CONNECT_AMI_ADMIN_CLIENT_ID": PUBLIC_PRO_CONNECT_AMI_ADMIN_CLIENT_ID,
            "PUBLIC_PRO_CONNECT_BASE_URL": PUBLIC_PRO_CONNECT_BASE_URL,
            "PUBLIC_PRO_CONNECT_AMI_ADMIN_REDIRECT_URL": PUBLIC_PRO_CONNECT_AMI_ADMIN_REDIRECT_URL,
            "PUBLIC_PRO_CONNECT_AUTHORIZATION_ENDPOINT": PUBLIC_PRO_CONNECT_AUTHORIZATION_ENDPOINT,
        },
    )


@get(path="/login-callback", include_in_schema=False)
async def login_callback(
    code: str,
    state_pro_connect: Annotated[str, Parameter(query="state")],
    request: Request[Any, Any, Any],
) -> Response[Any]:
    # 2.3.2. Vérification du state

    # 2.3.3. Génération du token
    redirect_uri: str = PUBLIC_PRO_CONNECT_AMI_ADMIN_REDIRECT_URL
    client_id: str = PUBLIC_PRO_CONNECT_AMI_ADMIN_CLIENT_ID
    client_secret: str = PRO_CONNECT_AMI_ADMIN_CLIENT_SECRET
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

    token_endpoint_headers: dict[str, str] = {"Content-Type": "application/x-www-form-urlencoded"}
    response: Any = httpx.post(
        f"{PUBLIC_PRO_CONNECT_BASE_URL}{PUBLIC_PRO_CONNECT_TOKEN_ENDPOINT}",
        headers=token_endpoint_headers,
        data=data,
    )
    if response.status_code != 200:
        return error_from_response(
            response, ami_details="ProConnect - Step 2.3.3. Génération du token " + str(data)
        )
    response_token_data: dict[str, str] = response.json()

    # 2.3.4. Vérification de l'id_token et du nonce
    httpx.get(f"{PUBLIC_PRO_CONNECT_BASE_URL}{PUBLIC_PRO_CONNECT_JWKS_ENDPOINT}")

    # 2.3.5. Stockage du id_token
    access_token = response_token_data["access_token"]
    id_token = response_token_data["id_token"]
    request.session["id_token"] = id_token

    # 2.3.6. Récupération des user info
    userinfo_endpoint_headers = {"Authorization": f"Bearer {access_token}"}
    response = httpx.get(
        f"{PUBLIC_PRO_CONNECT_BASE_URL}{PUBLIC_PRO_CONNECT_USERINFO_ENDPOINT}",
        headers=userinfo_endpoint_headers,
    )
    userinfo_jws = response.text
    userinfo = jwt.decode(userinfo_jws, options={"verify_signature": False}, algorithms=["ES256"])

    request.session["userinfo"] = userinfo
    if "redirect_once_connected" in request.session:
        return Redirect(request.session["redirect_once_connected"])
    return Redirect("/ami_admin")


@get(path="/logout", include_in_schema=False)
async def logout(request: Request[Any, Any, Any]) -> Response[Any]:
    if ami_admin_auth.is_not_connected(request.session):
        return Redirect("/ami_admin")

    logout_url: str = f"{PUBLIC_PRO_CONNECT_BASE_URL}{PUBLIC_PRO_CONNECT_LOGOUT_ENDPOINT}"
    redirect_url = f"{PUBLIC_API_URL}/ami_admin/logout-callback/"
    data: dict[str, str] = {
        "id_token_hint": request.session.get("id_token", ""),
        "state": "state-not-implemented-yet-and-has-more-than-32-chars",
        "post_logout_redirect_uri": redirect_url,
    }

    # Redirect the user to ProConnect's logout service. The local session cleanup happens in `/logout-callback`.
    return Redirect(logout_url, query_params=data)


@get(path="/logout-callback", include_in_schema=False)
async def logout_callback(
    state_pro_connect: Annotated[str, Parameter(query="state")],
    request: Request[Any, Any, Any],
) -> Response[Any]:
    # Local session cleanup: the user was logged out from ProConnect.
    del request.session["userinfo"]
    del request.session["id_token"]
    return Redirect("/ami_admin/logged_out")


@get(path="/logged_out", include_in_schema=False)
async def logged_out() -> Template:
    return Template(template_name="ami-admin/logged-out.html")


@get(
    path="/liste-des-usagers", guards=[ami_admin_auth.authenticated_guard], include_in_schema=False
)
async def list_users(db_session: AsyncSession) -> Template:
    users_service: UserService = UserService(session=db_session, load=[User.notifications])
    users = await users_service.list()
    return Template(
        template_name="ami-admin/list-users.html",
        context={"users": users, "isProConnected": True},
    )


@get(
    path="/test/user/{user_id: uuid}/send-notification",
    guards=[ami_admin_auth.authenticated_guard],
    include_in_schema=False,
)
async def send_notification(user_id: uuid.UUID, db_session: AsyncSession) -> Template:
    users_service: UserService = UserService(session=db_session)
    user = await users_service.get_one_or_none(id=user_id)
    if user is None:
        raise NotFoundException(detail="User not found")
    notifications_service: NotificationService = NotificationService(session=db_session)
    notifications = await notifications_service.list(
        order_by=(Notification.created_at, True),
        user=user,
    )
    return Template(
        template_name="ami-admin/send-notification.html",
        context={"user": user, "notifications": notifications, "isProConnected": True},
    )


def error_from_response(response: Response[str], ami_details: str | None = None) -> Response[str]:
    details = response.json()  # type: ignore[reportUnknownVariableType]
    if ami_details is not None:
        details["ami_details"] = ami_details
    return Response(details, status_code=response.status_code)  # type: ignore[reportUnknownVariableType]


def error_from_message(
    message: dict[str, str], status_code: int | None
) -> Response[dict[str, str]]:
    return Response(message, status_code=status_code)


ami_admin_router: Router = Router(
    path="/ami_admin",
    route_handlers=[
        home,
        login_callback,
        logout,
        logout_callback,
        logged_out,
        list_users,
        send_notification,
        create_static_files_router(
            path="/static",
            directories=[HTML_DIR],
            html_mode=True,
        ),
    ],
    exception_handlers={
        ami_admin_auth.NotAuthenticatedException: ami_admin_auth.redirect_to_login_exception_handler
    },
)
