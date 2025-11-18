import uuid
from typing import Annotated, Any

import jwt
from litestar import Controller, Request, Response, get
from litestar.params import Parameter
from litestar.response.redirect import Redirect
from litestar.status_codes import HTTP_500_INTERNAL_SERVER_ERROR

from app import env
from app.auth import generate_nonce
from app.httpx import httpxClient
from app.utils import error_from_message, retry_fc_later


class AuthController(Controller):
    @get(path="/login-france-connect", include_in_schema=False)
    async def login_france_connect(self, request: Request[Any, Any, Any]) -> Response[Any]:
        NONCE = generate_nonce()
        STATE = str(uuid.uuid4())
        request.session["nonce"] = NONCE
        request.session["state"] = STATE

        params = {
            "scope": "openid identite_pivot preferred_username email cnaf_quotient_familial",
            "redirect_uri": env.PUBLIC_FC_PROXY or env.PUBLIC_FC_AMI_REDIRECT_URL,
            "response_type": "code",
            "client_id": env.PUBLIC_FC_AMI_CLIENT_ID,
            # If we're in production, there's no proxy, just send the STATE.
            "state": (
                f"{env.PUBLIC_FC_AMI_REDIRECT_URL}?state={STATE}" if env.PUBLIC_FC_PROXY else STATE
            ),
            "nonce": NONCE,
            "acr_values": "eidas1",
            "prompt": "login",
        }

        login_url = f"{env.PUBLIC_FC_BASE_URL}{env.PUBLIC_FC_AUTHORIZATION_ENDPOINT}"
        return Redirect(login_url, query_params=params)

    @get(path="/login-callback", include_in_schema=False)
    async def login_callback(
        self,
        code: str | None,
        error: str | None,
        error_description: str | None,
        fc_state: Annotated[str, Parameter(query="state")],
        request: Request[Any, Any, Any],
    ) -> Response[Any]:
        if error or not code:
            return retry_fc_later(
                error_dict={
                    "error": error or "Erreur lors de la connexion",
                    "error_description": error_description or "",
                }
            )

        # Validate that the STATE is coherent with the one we sent to FC
        if not fc_state or fc_state != request.session.get("state", ""):
            return retry_fc_later()

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
        token_endpoint_headers: dict[str, str] = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        response: Any = httpxClient.post(
            f"{env.PUBLIC_FC_BASE_URL}{env.PUBLIC_FC_TOKEN_ENDPOINT}",
            headers=token_endpoint_headers,
            data=data,
        )
        if response.status_code != 200:
            return retry_fc_later()

        response_token_data: dict[str, str] = response.json()

        id_token: str = response_token_data.get("id_token", "")
        decoded_token: dict[str, str] = jwt.decode(
            id_token, options={"verify_signature": False}, algorithms=["ES256"]
        )

        # Validate that the NONCE is coherent with the one we sent to FC
        if "nonce" not in decoded_token or decoded_token["nonce"] != request.session.get(
            "nonce", ""
        ):
            return retry_fc_later()

        params: dict[str, str] = {
            **response_token_data,
            "is_logged_in": "true",
        }

        # Cleanup FC verifications
        del request.session["nonce"]
        del request.session["state"]

        return Redirect(f"{env.PUBLIC_APP_URL}/", query_params=params)
