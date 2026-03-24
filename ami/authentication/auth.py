import datetime
import uuid
from base64 import urlsafe_b64encode
from typing import Any
from uuid import uuid4

import jwt
from django.conf import settings
from django.utils.timezone import now

from ami.authentication.exception import FCError
from ami.authentication.models import Nonce
from ami.utils.httpx import AsyncClient


def generate_nonce() -> str:
    """Generate a NONCE by concatenating:
    - a uuid4 (for randomness and high confidence of uniqueness)
    - the curent timestamp (for sequentiality)

    The result is then base64 encoded.

    """
    _uuid = uuid4()
    _now = now()
    return urlsafe_b64encode(f"{_uuid}-{_now}".encode()).decode()


def create_jwt_token(user_id: str, jti: str) -> str:
    payload = {
        "sub": user_id,
        "jti": jti,
        "iat": now(),
        "exp": now() + datetime.timedelta(days=365 * 10),
    }
    return jwt.encode(payload, settings.AUTH_COOKIE_JWT_SECRET, algorithm="HS256")


def decode_jwt_token(token: str) -> dict | None:
    try:
        return jwt.decode(
            token,
            settings.AUTH_COOKIE_JWT_SECRET,
            algorithms=["HS256"],
        )
    except jwt.DecodeError:
        return None


async def get_fc_token(
    *, code: str, fc_state: str, client_secret: str, httpx_async_client: AsyncClient
) -> dict:
    # Validate that the STATE is coherent with the one we sent to FC
    if not fc_state:
        raise FCError("missing_state")
    try:
        state_uuid = uuid.UUID(fc_state)
    except ValueError:
        raise FCError("invalid_state")

    nonce = await Nonce.objects.filter(id=state_uuid).afirst()
    if not nonce:
        raise FCError("invalid_state")
    # Cleanup nonce as it was used
    await nonce.adelete()

    # FC - Step 5
    redirect_uri: str = settings.PUBLIC_FC_PROXY or settings.FC_AMI_REDIRECT_URL
    client_id: str = settings.FC_AMI_CLIENT_ID
    data: dict[str, str] = {
        "grant_type": "authorization_code",
        "redirect_uri": redirect_uri,
        "client_id": client_id,
        "client_secret": client_secret,
        "code": code,
    }

    # FC - Step 6
    token_endpoint_headers: dict[str, str] = {"Content-Type": "application/x-www-form-urlencoded"}
    response: Any = await httpx_async_client.post(
        f"{settings.PUBLIC_FC_BASE_URL}{settings.FC_TOKEN_ENDPOINT}",
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
