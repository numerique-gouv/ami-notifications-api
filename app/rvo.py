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


@get(path="/", include_in_schema=False)
async def home() -> Template:
    encours = []
    return Template(
        template_name="rvo-liste.html",
        context={
            "encours": encours,
            "isFranceConnected": True,
            "PUBLIC_FC_SERVICE_PROVIDER_CLIENT_ID": PUBLIC_FC_SERVICE_PROVIDER_CLIENT_ID,
            "PUBLIC_FC_BASE_URL": PUBLIC_FC_BASE_URL,
            "PUBLIC_FC_SERVICE_PROVIDER_REDIRECT_URL": PUBLIC_FC_SERVICE_PROVIDER_REDIRECT_URL,
            "PUBLIC_FC_AUTHORIZATION_ENDPOINT": PUBLIC_FC_AUTHORIZATION_ENDPOINT,
        },
    )


@get(path="/ami-fs-test-login-callback", include_in_schema=False)
async def ami_fs_test_login_callback(
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
            {"error": "Client secret not provided in .env file"}, HTTP_500_INTERNAL_SERVER_ERROR
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
    userinfo_endpoint_headers = {"Authorization": f"Bearer {access_token}"}
    response = httpx.get(
        f"{PUBLIC_FC_BASE_URL}{PUBLIC_FC_USERINFO_ENDPOINT}",
        headers=userinfo_endpoint_headers,
    )
    userinfo_jws = response.text
    userinfo = jwt.decode(userinfo_jws, options={"verify_signature": False}, algorithms=["ES256"])

    # FC - Step 16.1
    request.session["userinfo"] = userinfo
    return Redirect("/rvo")


def error_from_response(response: Response[str], ami_details: str | None = None) -> Response[str]:
    details = response.json()  # type: ignore[reportUnknownVariableType]
    if ami_details is not None:
        details["ami_details"] = ami_details
    return Response(details, status_code=response.status_code)  # type: ignore[reportUnknownVariableType]


def error_from_message(
    message: dict[str, str], status_code: int | None
) -> Response[dict[str, str]]:
    return Response(message, status_code=status_code)


rvo_router = Router(path="/rvo", route_handlers=[home])
# TODO : route ami_fs_test_login_callback
