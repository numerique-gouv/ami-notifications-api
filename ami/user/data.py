import uuid
from typing import Any

import jwt
from django.conf import settings
from django.utils.timezone import now

from ami.authentication.exception import FCError
from ami.user.models import User
from ami.user.utils import build_fc_hash
from ami.utils.httpx import httpxClient


def get_fc_userinfo(*, token_type: str, access_token: str) -> tuple[dict[str, str], uuid.UUID]:
    response = httpxClient.get(
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

    user, created = User.objects.get_or_create(fc_hash=fc_hash, defaults={"last_logged_in": now()})
    if created:
        create_welcome = True
    else:
        create_welcome = user.last_logged_in is None
        User.objects.filter(pk=user.pk).update(last_logged_in=now())
    if create_welcome:
        # XXX create welcome scheduled notification
        pass
    result: dict[str, Any] = {
        "user_data": userinfo_jws,
        "user_first_login": "true" if create_welcome else "false",
        "user_fc_hash": fc_hash,
    }

    return result, user.id
