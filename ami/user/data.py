import json
import logging
import uuid
from base64 import urlsafe_b64encode
from typing import Any

import jwt
from django.conf import settings
from django.utils.timezone import now

from ami.authentication.exception import FCError
from ami.authentication.schemas import data_providers
from ami.notification.models import ScheduledNotification
from ami.user.models import User
from ami.user.utils import build_fc_hash
from ami.utils.httpx import AsyncClient, Response
from ami.utils.jwks_client import get_jwks_client

logger = logging.getLogger(__name__)


async def get_fc_userinfo(
    *, token_type: str, access_token: str, httpx_async_client: AsyncClient
) -> tuple[dict[str, str], uuid.UUID]:
    response = await httpx_async_client.get(
        f"{settings.PUBLIC_FC_BASE_URL}{settings.FC_USERINFO_ENDPOINT}",
        headers={"authorization": f"{token_type} {access_token}"},
    )
    if response.status_code != 200:
        raise FCError(code=None)

    userinfo_jws = response.text
    signing_key = get_jwks_client().get_signing_key_from_jwt(userinfo_jws)
    decoded_userinfo = jwt.decode(
        userinfo_jws, key=signing_key, options={"verify_aud": False}, algorithms=["ES256"]
    )

    decoded_user_data = {
        k: v
        for k, v in decoded_userinfo.items()
        if k not in ["sub", "given_name_array", "aud", "exp", "iat", "iss"]
    }
    fc_hash = build_fc_hash(
        given_name=decoded_user_data["given_name"],
        family_name=decoded_user_data["family_name"],
        birthdate=decoded_user_data["birthdate"],
        gender=decoded_user_data["gender"],
        birthplace=decoded_user_data["birthplace"],
        birthcountry=decoded_user_data["birthcountry"],
    )
    decoded_user_data["sub"] = fc_hash

    user, created = await User.objects.aget_or_create(
        fc_hash=fc_hash, defaults={"last_logged_in": now()}
    )
    if created:
        create_welcome = True
    else:
        create_welcome = user.last_logged_in is None
        await User.objects.filter(pk=user.pk).aupdate(last_logged_in=now())

    if create_welcome:
        await ScheduledNotification.acreate_welcome_scheduled_notification(user)

    result: dict[str, Any] = {
        "user_data": userinfo_jws,
        "decoded_user_data": decoded_user_data,
        "user_first_login": "true" if create_welcome else "false",
        "user_fc_hash": fc_hash,
    }

    return result, user.id


async def call_data_provider(
    *,
    token_type: str,
    access_token: str,
    provider_id: str,
    httpx_async_client: AsyncClient,
) -> Response:
    response = await httpx_async_client.get(
        data_providers[provider_id].url,
        headers={"authorization": f"{token_type} {access_token}"},
    )
    return response


async def call_api_particulier_quotient(
    *,
    token_type: str,
    access_token: str,
    httpx_async_client: AsyncClient,
) -> Response:
    response = await call_data_provider(
        token_type=token_type,
        access_token=access_token,
        provider_id="api_particulier_quotient",
        httpx_async_client=httpx_async_client,
    )
    return response


async def get_api_particulier_quotient_raw_data(
    *,
    token_type: str,
    access_token: str,
    httpx_async_client: AsyncClient,
) -> str | None:
    response = await call_api_particulier_quotient(
        token_type=token_type, access_token=access_token, httpx_async_client=httpx_async_client
    )
    return urlsafe_b64encode(json.dumps(response.json()).encode()).decode()


async def get_address_from_api_particulier_quotient(
    *,
    token_type: str,
    access_token: str,
    httpx_async_client: AsyncClient,
) -> str | None:
    response = await call_api_particulier_quotient(
        token_type=token_type, access_token=access_token, httpx_async_client=httpx_async_client
    )
    if response.status_code != 200:
        log_error_to_sentry(response)
        return None
    data = response.json()
    if data.get("data", {}).get("adresse", {}):
        address_fields = ["numero_libelle_voie", "lieu_dit", "code_postal_ville", "pays"]
        address = {k: v or "" for k, v in data["data"]["adresse"].items() if k in address_fields}
        return urlsafe_b64encode(json.dumps(address).encode()).decode()


def log_error_to_sentry(response):
    extra = {
        "status_code": response.status_code,
        "response_text": response.text,
        "headers": response.headers,
    }
    try:
        extra["response_json"] = response.json()
    except json.JSONDecodeError:
        pass
    try:
        extra["X-Request-Id"] = response.headers.get("X-Request-Id")
    except ValueError:
        pass
    logger.error("Error", extra=extra)
