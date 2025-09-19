import os
from typing import Any

import httpx
import jwt
from litestar import (
    Request,
    Response,
    Router,
    get,
)
from litestar.response import Template
from litestar.response.redirect import Redirect
from litestar.status_codes import (
    HTTP_404_NOT_FOUND,
    HTTP_500_INTERNAL_SERVER_ERROR,
)

PUBLIC_FC_SERVICE_PROVIDER_CLIENT_ID = os.getenv("PUBLIC_FC_SERVICE_PROVIDER_CLIENT_ID", "")
FC_SERVICE_PROVIDER_CLIENT_SECRET = os.getenv("FC_SERVICE_PROVIDER_CLIENT_SECRET", "")
PUBLIC_FC_BASE_URL = os.getenv("PUBLIC_FC_BASE_URL", "")
PUBLIC_FC_SERVICE_PROVIDER_REDIRECT_URL = os.getenv("PUBLIC_FC_SERVICE_PROVIDER_REDIRECT_URL", "")
PUBLIC_FC_AUTHORIZATION_ENDPOINT = os.getenv("PUBLIC_FC_AUTHORIZATION_ENDPOINT", "")
PUBLIC_FC_TOKEN_ENDPOINT = os.getenv("PUBLIC_FC_TOKEN_ENDPOINT", "")
PUBLIC_FC_JWKS_ENDPOINT = os.getenv("PUBLIC_FC_JWKS_ENDPOINT", "")
PUBLIC_FC_USERINFO_ENDPOINT = os.getenv("PUBLIC_FC_USERINFO_ENDPOINT", "")
PUBLIC_FC_LOGOUT_ENDPOINT = os.getenv("PUBLIC_FC_LOGOUT_ENDPOINT", "")
PUBLIC_API_URL = os.getenv("PUBLIC_API_URL", "")


MEETING_LIST: list[dict[str, str]] = [
    {
        "id": "1",
        "when": "2 août 2025 à 15H15",
        "who": "France Travail",
        "where": "dans votre Agence France Travail Paris 18e Ney",
        "text": "Rendez-vous dans votre Agence France Travail Paris 18e Ney",
    },
    {
        "id": "2",
        "when": "25 novembre 2025 à 14H00",
        "who": "France Services",
        "where": "dans votre Maison France Services",
        "text": "Rendez-vous dans votre Maison France Services",
    },
]


@get(path="/", include_in_schema=False)
async def home(request: Request[Any, Any, Any]) -> Template:
    return Template(
        template_name="rvo-liste.html",
        context={
            "isFranceConnected": "userinfo" in request.session and "id_token" in request.session,
            "PUBLIC_FC_SERVICE_PROVIDER_CLIENT_ID": PUBLIC_FC_SERVICE_PROVIDER_CLIENT_ID,
            "PUBLIC_FC_BASE_URL": PUBLIC_FC_BASE_URL,
            "PUBLIC_FC_SERVICE_PROVIDER_REDIRECT_URL": PUBLIC_FC_SERVICE_PROVIDER_REDIRECT_URL,
            "PUBLIC_FC_AUTHORIZATION_ENDPOINT": PUBLIC_FC_AUTHORIZATION_ENDPOINT,
            "object_list": MEETING_LIST,
        },
    )


@get(path="/login-callback", include_in_schema=False)
async def login_callback(
    code: str,
    request: Request[Any, Any, Any],
) -> Response[Any]:
    # FC - Step 5
    redirect_uri: str = f"{PUBLIC_FC_SERVICE_PROVIDER_REDIRECT_URL}"
    client_id: str = PUBLIC_FC_SERVICE_PROVIDER_CLIENT_ID
    client_secret: str = FC_SERVICE_PROVIDER_CLIENT_SECRET
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

    # FC - Step 8
    httpx.get(f"{PUBLIC_FC_BASE_URL}{PUBLIC_FC_JWKS_ENDPOINT}")

    # FC - Step 11
    access_token = response_token_data["access_token"]
    id_token = response_token_data["id_token"]
    userinfo_endpoint_headers = {"Authorization": f"Bearer {access_token}"}
    response = httpx.get(
        f"{PUBLIC_FC_BASE_URL}{PUBLIC_FC_USERINFO_ENDPOINT}",
        headers=userinfo_endpoint_headers,
    )
    userinfo_jws = response.text
    userinfo = jwt.decode(userinfo_jws, options={"verify_signature": False}, algorithms=["ES256"])

    # FC - Step 16.1
    request.session["userinfo"] = userinfo
    request.session["id_token"] = id_token
    if "redirect_once_connected" in request.session:
        return Redirect(request.session["redirect_once_connected"])
    return Redirect("/rvo")


@get(path="/logout", include_in_schema=False)
async def logout(request: Request[Any, Any, Any]) -> Response[Any]:
    if is_not_connected(request.session):
        return Redirect("/rvo")

    logout_url: str = f"{PUBLIC_FC_BASE_URL}{PUBLIC_FC_LOGOUT_ENDPOINT}"
    data: dict[str, str] = {
        "id_token_hint": request.session.get("id_token", ""),
        "state": "not-implemented-yet-and-has-more-than-32-chars",
        "post_logout_redirect_uri": f"{PUBLIC_API_URL}/rvo/logout-callback",
    }

    # Redirect the user to FC's logout service. The local session cleanup happens in `/logout-callback`.
    return Redirect(logout_url, query_params=data)


@get(path="/logout-callback", include_in_schema=False)
async def logout_callback(request: Request[Any, Any, Any]) -> Response[Any]:
    # Local session cleanup: the user was logged out from FC.
    del request.session["userinfo"]
    del request.session["id_token"]
    return Redirect("/rvo/logged_out")


@get(path="/logged_out", include_in_schema=False)
async def logged_out() -> Template:
    return Template(template_name="rvo-logged-out.html")


@get(path="/detail/{detail_id: str}", include_in_schema=False)
async def detail(detail_id: str, request: Request[Any, Any, Any]) -> Response[Any] | Template:
    if is_not_connected(request.session):
        request.session["redirect_once_connected"] = str(request.url)
        print("redirect_once_connected", request.url)
        return Redirect("/rvo")

    if "redirect_once_connected" in request.session:
        del request.session["redirect_once_connected"]  # Not useful anymore.

    meeting_list: dict[str, dict[str, str]] = {meeting["id"]: meeting for meeting in MEETING_LIST}
    if detail_id not in meeting_list:
        return error_from_message(
            {"error": "Not found."},
            HTTP_404_NOT_FOUND,
        )
    detail: dict[str, str] = meeting_list[detail_id]
    return Template(
        template_name="rvo-detail.html",
        context={
            "detail": detail,
        },
    )


def is_not_connected(session: dict[str, Any]) -> bool:
    return "userinfo" not in session or "id_token" not in session


def error_from_response(response: Response[str], ami_details: str | None = None) -> Response[str]:
    details = response.json()  # type: ignore[reportUnknownVariableType]
    if ami_details is not None:
        details["ami_details"] = ami_details
    return Response(details, status_code=response.status_code)  # type: ignore[reportUnknownVariableType]


def error_from_message(
    message: dict[str, str], status_code: int | None
) -> Response[dict[str, str]]:
    return Response(message, status_code=status_code)


rvo_router: Router = Router(
    path="/rvo", route_handlers=[home, login_callback, logout, logout_callback, logged_out, detail]
)
