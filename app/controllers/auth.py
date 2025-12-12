import uuid
from typing import Annotated, Any

import jwt
from advanced_alchemy.extensions.litestar import providers
from litestar import Controller, Request, Response, get, post
from litestar.params import Parameter
from litestar.response.redirect import Redirect
from litestar.status_codes import HTTP_500_INTERNAL_SERVER_ERROR

from app import env
from app.auth import generate_nonce, jwt_cookie_auth
from app.httpx import httpxClient
from app.services.nonce import NonceService
from app.utils import error_from_message, retry_fc_later


class AuthController(Controller):
    dependencies = {
        "nonces_service": providers.create_service_provider(NonceService),
    }

    @get(path="/login-france-connect", include_in_schema=False, exclude_from_auth=True)
    async def login_france_connect(
        self,
        nonces_service: NonceService,
        request: Request[Any, Any, Any],
    ) -> Response[Any]:
        NONCE = generate_nonce()
        nonce = await nonces_service.create({"nonce": NONCE})

        params = {
            "scope": env.PUBLIC_FC_SCOPE,
            "redirect_uri": env.PUBLIC_FC_PROXY or env.PUBLIC_FC_AMI_REDIRECT_URL,
            "response_type": "code",
            "client_id": env.PUBLIC_FC_AMI_CLIENT_ID,
            # If we're in production, there's no proxy, just send the STATE.
            "state": (
                f"{env.PUBLIC_FC_AMI_REDIRECT_URL}?state={nonce.id}"
                if env.PUBLIC_FC_PROXY
                else str(nonce.id)
            ),
            "nonce": NONCE,
            "acr_values": "eidas1",
            "prompt": "login",
        }

        login_url = f"{env.PUBLIC_FC_BASE_URL}{env.PUBLIC_FC_AUTHORIZATION_ENDPOINT}"
        return Redirect(login_url, query_params=params)

    @get(path="/login-callback", include_in_schema=False, exclude_from_auth=True)
    async def login_callback(
        self,
        nonces_service: NonceService,
        code: str | None,
        error: str | None,
        error_description: str | None,
        fc_state: Annotated[str, Parameter(query="state")],
        request: Request[Any, Any, Any],
    ) -> Response[Any]:
        if error or not code:
            return retry_fc_later(
                error_dict={
                    "error_code": "fc_error",
                    "error": error or "Erreur lors de la connexion",
                    "error_description": error_description or "",
                }
            )

        # Validate that the STATE is coherent with the one we sent to FC
        if not fc_state:
            return retry_fc_later(error_dict={"error_code": "missing_state"})
        try:
            state = uuid.UUID(fc_state)
        except ValueError:
            return retry_fc_later(error_dict={"error_code": "invalid_state"})
        nonce = await nonces_service.get_one_or_none(id=state)
        if not nonce:
            return retry_fc_later(error_dict={"error_code": "invalid_state"})
        # Cleanup nonce as it was used
        await nonces_service.delete(nonce.id)

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
        if not id_token:
            # XXX this is not covered by tests for the moment
            return retry_fc_later(error_dict={"error_code": "missing_id_token"})
        decoded_token: dict[str, str] = jwt.decode(
            id_token, options={"verify_signature": False}, algorithms=["ES256"]
        )

        # Validate that the NONCE is coherent with the one we sent to FC
        if "nonce" not in decoded_token:
            # XXX this is not covered by tests for the moment
            return retry_fc_later(error_dict={"error_code": "missing_nonce"})
        if decoded_token["nonce"] != nonce.nonce:
            return retry_fc_later(error_dict={"error_code": "invalid_nonce"})

        params: dict[str, str] = {
            **response_token_data,
            "is_logged_in": "true",
        }

        return Redirect(f"{env.PUBLIC_APP_URL}/", query_params=params)

    @post(path="/logout", include_in_schema=False)
    async def logout(self) -> Response[Any]:
        response = Response({})
        response.delete_cookie(key=jwt_cookie_auth.key)
        return response

    @get(path="/check-auth", include_in_schema=False)
    async def check_auth(self) -> dict[str, Any]:
        return {"authenticated": True}
