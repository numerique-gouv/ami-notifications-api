import asyncio
import datetime
import json
import uuid
from base64 import urlsafe_b64encode
from typing import Annotated, Any

import jwt
from advanced_alchemy.extensions.litestar import providers
from litestar import Controller, Request, Response, get, post
from litestar.params import Parameter
from litestar.response.redirect import Redirect
from litestar.status_codes import HTTP_500_INTERNAL_SERVER_ERROR

from app import env, models
from app.auth import generate_nonce, jwt_cookie_auth
from app.errors import TechnicalError
from app.httpx import AsyncClient
from app.services.nonce import NonceService
from app.services.scheduled_notification import ScheduledNotificationService
from app.services.user import UserService
from app.utils import build_fc_hash, error_from_message, retry_fc_later


class FCError(Exception):
    def __init__(self, code: str | None, *args: Any, **kwargs: Any):
        self.code = code
        super().__init__(*args, **kwargs)


class AuthController(Controller):
    dependencies = {
        "nonces_service": providers.create_service_provider(NonceService),
        "users_service": providers.create_service_provider(UserService),
        "scheduled_notifications_service": providers.create_service_provider(
            ScheduledNotificationService
        ),
    }

    @get(path="/login-france-connect", include_in_schema=False, exclude_from_auth=True)
    async def login_france_connect(
        self,
        nonces_service: NonceService,
        request: Request[Any, Any, Any],
    ) -> Response[Any]:
        try:
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
        except Exception as e:
            raise TechnicalError from e

    @get(path="/login-callback", include_in_schema=False, exclude_from_auth=True)
    async def login_callback(
        self,
        nonces_service: NonceService,
        users_service: UserService,
        scheduled_notifications_service: ScheduledNotificationService,
        code: str | None,
        error: str | None,
        error_description: str | None,
        fc_state: Annotated[str, Parameter(query="state")],
        request: Request[Any, Any, Any],
        httpx_async_client: AsyncClient,
    ) -> Response[Any]:
        try:
            if error or not code:
                return retry_fc_later(
                    error_dict={
                        "error_code": "fc_error",
                        "error": error or "Erreur lors de la connexion",
                        "error_description": error_description or "",
                    }
                )

            client_secret: str = env.FC_AMI_CLIENT_SECRET
            if client_secret == "":
                return error_from_message(
                    {"error": "Client secret not provided in .env.local file"},
                    HTTP_500_INTERNAL_SERVER_ERROR,
                )

            response_token_data: dict[str, str] = await self.get_fc_token(
                code=code,
                fc_state=fc_state,
                client_secret=client_secret,
                nonces_service=nonces_service,
                httpx_async_client=httpx_async_client,
            )
            id_token: str = response_token_data["id_token"]
            token_type = response_token_data.get("token_type", "")
            if not token_type:
                raise FCError("missing_token_type")
            access_token = response_token_data.get("access_token", "")
            if not access_token:
                raise FCError("missing_access_token")

            task_api_particulier = None
            try:
                async with asyncio.TaskGroup() as task_group:
                    task_userinfo = task_group.create_task(
                        self.get_fc_userinfo(
                            token_type=token_type,
                            access_token=access_token,
                            users_service=users_service,
                            scheduled_notifications_service=scheduled_notifications_service,
                            httpx_async_client=httpx_async_client,
                        )
                    )
                    if (
                        "cnaf_enfants" in env.PUBLIC_FC_SCOPE
                        and "cnaf_adresse" in env.PUBLIC_FC_SCOPE
                    ):
                        task_api_particulier = task_group.create_task(
                            self.get_address_from_api_particulier_quotient(
                                token_type=token_type,
                                access_token=access_token,
                                httpx_async_client=httpx_async_client,
                            )
                        )
            except* FCError as e:
                raise e.exceptions[0]

            user_data = {
                "is_logged_in": "true",
                "id_token": id_token,
            }
            userinfo_result, user_id = task_userinfo.result()
            user_data.update(userinfo_result)
            if task_api_particulier:
                address = task_api_particulier.result()
                if address:
                    user_data["address"] = address

            login = jwt_cookie_auth.login(
                identifier=str(user_id),
            )
            redirect = Redirect(f"{env.PUBLIC_APP_URL}/", query_params=user_data)
            redirect.cookies = login.cookies
            return redirect
        except FCError as e:
            if e.code is None:
                return retry_fc_later()
            return retry_fc_later(error_dict={"error_code": e.code})
        except Exception as e:
            raise TechnicalError from e

    async def get_fc_token(
        self,
        *,
        code: str,
        fc_state: str,
        client_secret: str,
        nonces_service: NonceService,
        httpx_async_client: AsyncClient,
    ):
        # Validate that the STATE is coherent with the one we sent to FC
        if not fc_state:
            raise FCError("missing_state")
        try:
            state = uuid.UUID(fc_state)
        except ValueError:
            raise FCError("invalid_state")
        nonce = await nonces_service.get_one_or_none(id=state)
        if not nonce:
            raise FCError("invalid_state")
        # Cleanup nonce as it was used
        await nonces_service.delete(nonce.id)

        # FC - Step 5
        redirect_uri: str = env.PUBLIC_FC_PROXY or env.PUBLIC_FC_AMI_REDIRECT_URL
        client_id: str = env.PUBLIC_FC_AMI_CLIENT_ID
        data: dict[str, str] = {
            "grant_type": "authorization_code",
            "redirect_uri": redirect_uri,
            "client_id": client_id,
            "client_secret": client_secret,
            "code": code,
        }

        # FC - Step 6
        token_endpoint_headers: dict[str, str] = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        response: Any = await httpx_async_client.post(
            f"{env.PUBLIC_FC_BASE_URL}{env.PUBLIC_FC_TOKEN_ENDPOINT}",
            headers=token_endpoint_headers,
            data=data,
        )
        if response.status_code != 200:
            raise FCError(code=None)

        response_token_data: dict[str, str] = response.json()

        id_token: str = response_token_data.get("id_token", "")
        if not id_token:
            raise FCError("missing_id_token")
        decoded_token: dict[str, str] = jwt.decode(
            id_token, options={"verify_signature": False}, algorithms=["ES256"]
        )

        # Validate that the NONCE is coherent with the one we sent to FC
        if "nonce" not in decoded_token:
            raise FCError("missing_nonce")
        if decoded_token["nonce"] != nonce.nonce:
            raise FCError("invalid_nonce")

        return response_token_data

    async def get_fc_userinfo(
        self,
        *,
        token_type: str,
        access_token: str,
        users_service: UserService,
        scheduled_notifications_service: ScheduledNotificationService,
        httpx_async_client: AsyncClient,
    ) -> tuple[dict[str, str], uuid.UUID]:
        response = await httpx_async_client.get(
            f"{env.PUBLIC_FC_BASE_URL}{env.PUBLIC_FC_USERINFO_ENDPOINT}",
            headers={"authorization": f"{token_type} {access_token}"},
        )
        if response.status_code != 200:
            raise FCError(code=None)

        userinfo_jws = response.text
        decoded_userinfo = jwt.decode(
            userinfo_jws, options={"verify_signature": False}, algorithms=["ES256"]
        )
        fc_hash = build_fc_hash(
            given_name=decoded_userinfo["given_name"],
            family_name=decoded_userinfo["family_name"],
            birthdate=decoded_userinfo["birthdate"],
            gender=decoded_userinfo["gender"],
            birthplace=decoded_userinfo["birthplace"],
            birthcountry=decoded_userinfo["birthcountry"],
        )

        user: models.User | None = await users_service.get_one_or_none(fc_hash=fc_hash)
        create_welcome = False
        now = datetime.datetime.now(datetime.timezone.utc)
        if user is None:
            user = await users_service.create(models.User(fc_hash=fc_hash, last_logged_in=now))
            create_welcome = True
        else:
            create_welcome = user.last_logged_in is None
            user = await users_service.update({"last_logged_in": now}, item_id=user.id)
        if create_welcome:
            await scheduled_notifications_service.create_welcome_scheduled_notification(user)
        result: dict[str, Any] = {
            "user_data": userinfo_jws,
            "user_first_login": "true" if create_welcome else "false",
            "user_fc_hash": fc_hash,
        }

        return result, user.id

    async def get_address_from_api_particulier_quotient(
        self,
        *,
        token_type: str,
        access_token: str,
        httpx_async_client: AsyncClient,
    ) -> str | None:
        response = await httpx_async_client.get(
            f"{env.PUBLIC_API_PARTICULIER_BASE_URL}{env.PUBLIC_API_PARTICULIER_QUOTIENT_ENDPOINT}?recipient={env.PUBLIC_API_PARTICULIER_RECIPIENT_ID}",
            headers={"authorization": f"{token_type} {access_token}"},
        )
        if response.status_code != 200:
            return None
        data = response.json()
        if data.get("data", {}).get("adresse", {}):
            address_fields = ["numero_libelle_voie", "lieu_dit", "code_postal_ville", "pays"]
            address = {
                k: v or "" for k, v in data["data"]["adresse"].items() if k in address_fields
            }
            return urlsafe_b64encode(json.dumps(address).encode("utf8")).decode("utf8")

    @post(path="/logout", include_in_schema=False)
    async def logout(self) -> Response[Any]:
        response = Response({})
        response.delete_cookie(key=jwt_cookie_auth.key)
        return response

    @get(path="/check-auth", include_in_schema=False)
    async def check_auth(self) -> dict[str, Any]:
        return {"authenticated": True}
