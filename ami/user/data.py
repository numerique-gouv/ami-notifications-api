import json
import uuid
from base64 import urlsafe_b64encode
from typing import Any

import jwt
from django.conf import settings
from django.utils.timezone import now

from ami.authentication.exception import FCError
from ami.notification.models import ScheduledNotification
from ami.user.models import User
from ami.user.utils import build_fc_hash
from ami.utils.httpx import AsyncClient


async def get_fc_userinfo(
    *, token_type: str, access_token: str, httpx_async_client: AsyncClient
) -> tuple[dict[str, str], uuid.UUID]:
    response = await httpx_async_client.get(
        f"{settings.PUBLIC_FC_BASE_URL}{settings.PUBLIC_FC_USERINFO_ENDPOINT}",
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
        "user_first_login": "true" if create_welcome else "false",
        "user_fc_hash": fc_hash,
    }

    return result, user.id


async def get_address_from_api_particulier_quotient(
    *,
    token_type: str,
    access_token: str,
    httpx_async_client: AsyncClient,
) -> str | None:
    response = await httpx_async_client.get(
        f"{settings.PUBLIC_API_PARTICULIER_BASE_URL}{settings.PUBLIC_API_PARTICULIER_QUOTIENT_ENDPOINT}"
        f"?recipient={settings.PUBLIC_API_PARTICULIER_RECIPIENT_ID}",
        headers={"authorization": f"{token_type} {access_token}"},
    )
    if response.status_code != 200:
        return None
    data = response.json()
    if data.get("data", {}).get("adresse", {}):
        address_fields = ["numero_libelle_voie", "lieu_dit", "code_postal_ville", "pays"]
        address = {k: v or "" for k, v in data["data"]["adresse"].items() if k in address_fields}
        return urlsafe_b64encode(json.dumps(address).encode("utf8")).decode("utf8")
