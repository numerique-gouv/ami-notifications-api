import asyncio
import uuid
from urllib.parse import urlencode

from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import redirect
from django.views.decorators.http import require_GET

from ami.authentication.auth import create_jwt_token, generate_nonce, get_fc_token
from ami.authentication.exception import FCError
from ami.authentication.models import Nonce
from ami.user.data import get_address_from_api_particulier_quotient, get_fc_userinfo
from ami.utils.httpx import httpxAsyncClient


def retry_fc_later(error_dict: dict | None = None):
    error_dict = error_dict or {}
    params: dict[str, str] = {
        "error": "Erreur lors de la FranceConnexion, veuillez réessayer plus tard.",
        "error_type": "FranceConnect",
        **error_dict,
    }
    return redirect(f"{settings.PUBLIC_APP_URL}/?{urlencode(params)}")


@require_GET
def login_france_connect(request):
    try:
        NONCE = generate_nonce()
        nonce = Nonce.objects.create(nonce=NONCE)

        params = {
            "scope": settings.PUBLIC_FC_SCOPE,
            "redirect_uri": settings.PUBLIC_FC_PROXY or settings.PUBLIC_FC_AMI_REDIRECT_URL,
            "response_type": "code",
            "client_id": settings.PUBLIC_FC_AMI_CLIENT_ID,
            "state": (
                f"{settings.PUBLIC_FC_AMI_REDIRECT_URL}?state={nonce.id}"
                if settings.PUBLIC_FC_PROXY
                else str(nonce.id)
            ),
            "nonce": NONCE,
            "acr_values": "eidas1",
            "prompt": "login",
        }

        login_url = (
            f"{settings.PUBLIC_FC_BASE_URL}{settings.PUBLIC_FC_AUTHORIZATION_ENDPOINT}"
            f"?{urlencode(params)}"
        )
        return redirect(login_url)
    except Exception:
        return redirect(f"{settings.PUBLIC_APP_URL}/#/technical-error")


@require_GET
async def login_callback(request):
    try:
        code = request.GET.get("code")
        error = request.GET.get("error")
        error_description = request.GET.get("error_description", "")
        fc_state = request.GET.get("state", "")

        if error or not code:
            return retry_fc_later(
                {
                    "error_code": "fc_error",
                    "error": error or "Erreur lors de la connexion",
                    "error_description": error_description,
                }
            )

        client_secret = settings.FC_AMI_CLIENT_SECRET
        if not client_secret:
            return JsonResponse({"error": "Client secret manquant"}, status=500)

        async with httpxAsyncClient() as httpx_async_client:
            response_token_data = await get_fc_token(
                code=code,
                fc_state=fc_state,
                client_secret=client_secret,
                httpx_async_client=httpx_async_client,
            )

            id_token = response_token_data["id_token"]
            token_type = response_token_data.get("token_type", "")
            if not token_type:
                raise FCError("missing_token_type")
            access_token = response_token_data.get("access_token", "")
            if not access_token:
                raise FCError("missing_access_token")

            try:
                async with asyncio.TaskGroup() as task_group:
                    task_userinfo = task_group.create_task(
                        get_fc_userinfo(
                            token_type=token_type,
                            access_token=access_token,
                            httpx_async_client=httpx_async_client,
                        )
                    )
                    task_api_particulier = None
                    if (
                        "cnaf_enfants" in settings.PUBLIC_FC_SCOPE
                        and "cnaf_adresse" in settings.PUBLIC_FC_SCOPE
                    ):
                        task_api_particulier = task_group.create_task(
                            get_address_from_api_particulier_quotient(
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

            jwt_token = create_jwt_token(user_id=str(user_id), jti=uuid.uuid4().hex)

            redirect_url = f"{settings.PUBLIC_APP_URL}/?{urlencode(user_data)}"
            response = redirect(redirect_url)
            response.set_cookie(
                key=settings.AUTH_COOKIE_JWT_NAME,
                value=f"Bearer {jwt_token}",
                max_age=365 * 10 * 24 * 3600,
                secure=True,
                httponly=True,
                samesite="None",
            )
            return response

    except FCError as e:
        if e.code is None:
            return retry_fc_later()
        return retry_fc_later({"error_code": e.code})
    except Exception:
        return redirect(f"{settings.PUBLIC_APP_URL}/#/technical-error")
