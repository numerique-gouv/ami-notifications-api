import asyncio
import base64
import json
import logging
import uuid
from urllib.parse import urlencode, urlparse

from django.conf import settings
from django.http import Http404, JsonResponse
from django.shortcuts import redirect
from django.views.decorators.http import require_GET
from rest_framework.decorators import api_view
from rest_framework.response import Response
from webauthn import (
    generate_authentication_options,
    generate_registration_options,
    options_to_json,
    verify_authentication_response,
    verify_registration_response,
)
from webauthn.helpers.structs import (
    AuthenticatorAttachment,
    AuthenticatorSelectionCriteria,
    ResidentKeyRequirement,
)

from ami.authentication.auth import create_jwt_token, generate_nonce, get_fc_scope, get_fc_token
from ami.authentication.decorators import ami_login_required
from ami.authentication.exception import FCError
from ami.authentication.models import Nonce, UserPasskey
from ami.authentication.schemas import data_providers
from ami.user.data import (
    get_address_from_api_particulier_quotient,
    get_api_particulier_quotient_raw_data,
    get_api_particulier_statut_etudiant_raw_data,
    get_fc_userinfo,
)
from ami.utils.httpx import httpxAsyncClient

logger = logging.getLogger(__name__)


data_provider_functions = {
    "api_particulier_quotient": get_api_particulier_quotient_raw_data,
    "api_particulier_statut_etudiant": get_api_particulier_statut_etudiant_raw_data,
}


def retry_fc_later(error_dict: dict | None = None):
    error_dict = error_dict or {}
    params: dict[str, str] = {
        "error": "Erreur lors de la FranceConnexion, veuillez réessayer plus tard.",
        "error_type": "FranceConnect",
        **error_dict,
    }
    return redirect(f"{settings.PUBLIC_APP_URL}/?{urlencode(params)}")


def login(request, login_type):
    try:
        context = None
        if login_type == "ami-fi":
            provider_ids = []
            if request.GET.get("provider_id") and request.GET["provider_id"] in data_providers:
                provider_ids.append(request.GET["provider_id"])
            context = {
                "idp": login_type,
                "provider_ids": provider_ids,
            }
            scope = get_fc_scope(provider_ids)
        elif login_type == "silent-ami-fi":
            scope = get_fc_scope([])
            redirect_url = request.GET.get("redirect_url")
            context = {
                "idp": login_type,
                "redirect_url": redirect_url or "",
            }
        else:
            scope = get_fc_scope(["api_particulier_quotient"])
        NONCE = generate_nonce()
        nonce = Nonce.objects.create(
            nonce=NONCE,
            context=context,
        )

        use_proxy = bool(settings.PUBLIC_FC_PROXY_BASE_URL)
        fi_login = login_type != "fc"

        redirect_uri: str = settings.FC_AMI_REDIRECT_URL
        state: str = str(nonce.id)
        if use_proxy:
            redirect_uri = f"{settings.PUBLIC_FC_PROXY_BASE_URL}/"
            state = f"{settings.FC_AMI_REDIRECT_URL}?state={nonce.id}"
        params = {
            "scope": scope,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "client_id": settings.FC_AMI_CLIENT_ID,
            "state": state,
            "nonce": NONCE,
            "acr_values": "eidas1",
            "prompt": "login",
        }
        if fi_login:
            params["idp_hint"] = settings.FI_IDP_ID

        login_url = (
            f"{settings.PUBLIC_FC_BASE_URL}{settings.FC_AUTHORIZATION_ENDPOINT}?{urlencode(params)}"
        )
        if use_proxy and fi_login:
            params = {
                "from_url": f"{settings.PUBLIC_APP_URL}/",
                "fc_url": login_url,
            }
            login_url = (
                f"{settings.PUBLIC_FC_PROXY_BASE_URL}/ami-fi-authorize-request/?{urlencode(params)}"
            )
        return redirect(login_url)
    except Exception as e:
        logging.exception(e)
        return redirect(f"{settings.PUBLIC_APP_URL}/#/technical-error")


@require_GET
def login_france_connect(request):
    return login(request, "fc")


@require_GET
def login_ami_fi(request):
    return login(request, "ami-fi")


@require_GET
def silent_login_ami_fi(request):
    if not settings.FI_SILENT_LOGIN_ENABLED:
        raise Http404
    return login(request, "silent-ami-fi")


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
            # get FC token
            response_token_data, nonce_context = await get_fc_token(
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

            # get user data: userinfo, data from providers, ...
            try:
                tasks = await get_user_data(
                    token_type=token_type,
                    access_token=access_token,
                    nonce_context=nonce_context,
                    httpx_async_client=httpx_async_client,
                )
            except* FCError as e:
                raise e.exceptions[0]

            # build user_data from previous calls
            user_data = {
                "is_logged_in": "true",
                "id_token": id_token,
            }
            user_id, userinfo_result = None, {}
            if "userinfo" in tasks:
                task_userinfo = tasks.pop("userinfo")
                userinfo_result, user_id = task_userinfo.result()
                user_data.update(userinfo_result)
                for key, task in tasks.items():
                    result = task.result()
                    if result:
                        user_data[key] = result

            # build redirect_url, depending on kind of login (fc, ami-fi, silent-ami-fi)
            redirect_url = f"{settings.PUBLIC_APP_URL}/?{urlencode(user_data)}"
            if nonce_context.get("idp") == "ami-fi":
                redirect_url = f"{settings.PUBLIC_APP_URL}/?{urlencode(user_data)}#/fi"
            if nonce_context.get("idp") == "silent-ami-fi":
                user_data["redirect_url"] = nonce_context.get("redirect_url") or ""
                redirect_url = f"{settings.PUBLIC_APP_URL}/?{urlencode(user_data)}#/silent-login"

            # set cookies only for fc
            response = redirect(redirect_url)
            if nonce_context.get("idp") in ["ami-fi", "silent-ami-fi"]:
                return response
            jwt_token = create_jwt_token(user_id=str(user_id), jti=uuid.uuid4().hex)
            response.set_cookie(
                key=settings.AUTH_COOKIE_JWT_NAME,
                value=f"Bearer {jwt_token}",
                max_age=365 * 10 * 24 * 3600,
                secure=True,
                httponly=True,
                samesite="None",
            )
            response.set_cookie(
                key=settings.USERINFO_COOKIE_JWT_NAME,
                value=userinfo_result["user_data"],
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
    except Exception as e:
        logging.exception(e)
        return redirect(f"{settings.PUBLIC_APP_URL}/#/technical-error")


async def get_user_data(*, token_type, access_token, nonce_context, httpx_async_client):
    tasks = {}

    if nonce_context.get("idp") == "silent-ami-fi":
        # don't call data providers
        return tasks

    async with asyncio.TaskGroup() as task_group:
        tasks["userinfo"] = task_group.create_task(
            get_fc_userinfo(
                token_type=token_type,
                access_token=access_token,
                httpx_async_client=httpx_async_client,
            )
        )
        if nonce_context.get("idp") == "ami-fi":
            # providers are in nonce context, set on login view
            for key in nonce_context.get("provider_ids") or []:
                provider = data_providers.get(key)
                if provider is not None and provider.is_enabled():
                    tasks[key] = task_group.create_task(
                        data_provider_functions[key](
                            token_type=token_type,
                            access_token=access_token,
                            httpx_async_client=httpx_async_client,
                        )
                    )
        elif data_providers["api_particulier_quotient"].is_enabled():
            # fc, only call api_particulier_quotient, if enabled
            tasks["address"] = task_group.create_task(
                get_address_from_api_particulier_quotient(
                    token_type=token_type,
                    access_token=access_token,
                    httpx_async_client=httpx_async_client,
                )
            )

    return tasks


@api_view(["GET"])
@ami_login_required
def passkey_generate_registration_options(request):
    options = generate_registration_options(
        rp_id=urlparse(settings.PUBLIC_APP_URL).hostname,
        rp_name="Example Co",
        user_name="fc-hash",
        authenticator_selection=AuthenticatorSelectionCriteria(
            authenticator_attachment=AuthenticatorAttachment.PLATFORM,
            resident_key=ResidentKeyRequirement.REQUIRED,
        ),
    )
    challenge = base64.encodebytes(options.challenge).decode()
    request.session["passkey_registration_challenge"] = challenge

    return Response(json.loads(options_to_json(options)))


@api_view(["POST"])
@ami_login_required
def passkey_verify_registration(request):
    challenge = request.session.get("passkey_registration_challenge")
    if not challenge:
        raise Exception("ho no ! challenge not found !")
    registration_verification = verify_registration_response(
        credential=request.data,
        expected_challenge=base64.decodebytes(challenge.encode()),
        expected_origin=settings.PUBLIC_APP_URL,
        expected_rp_id=urlparse(settings.PUBLIC_APP_URL).hostname,
        require_user_verification=True,
    )
    credential_id = (
        base64.encodebytes(registration_verification.credential_id).decode().split("=")[0]
    )
    public_key = base64.encodebytes(registration_verification.credential_public_key).decode()
    UserPasskey.objects.create(
        user=request.ami_user, credential_id=credential_id, credential_public_key=public_key
    )
    request.session.delete()
    return Response({"verified": registration_verification.user_verified})


@api_view(["GET"])
def passkey_generate_authentication_options(request):
    options = generate_authentication_options(
        rp_id=urlparse(settings.PUBLIC_APP_URL).hostname,
    )
    challenge = base64.encodebytes(options.challenge).decode()
    request.session["passkey_authentication_challenge"] = challenge
    return Response(json.loads(options_to_json(options)))


@api_view(["POST"])
def passkey_verify_authentication(request):
    challenge = request.session.get("passkey_authentication_challenge")
    if not challenge:
        raise Exception("ho no ! challenge not found !")
    credential_id = request.data["id"]
    user_passkey = UserPasskey.objects.get(credential_id=credential_id)
    authentication_verification = verify_authentication_response(
        credential=request.data,
        expected_challenge=base64.decodebytes(challenge.encode()),
        expected_origin=settings.PUBLIC_APP_URL,
        expected_rp_id=urlparse(settings.PUBLIC_APP_URL).hostname,
        credential_public_key=base64.decodebytes(user_passkey.credential_public_key.encode()),
        credential_current_sign_count=0,
        require_user_verification=True,
    )
    request.session.delete()
    return Response({"verified": authentication_verification.user_verified})
