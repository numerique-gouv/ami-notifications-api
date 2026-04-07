import time

from django.conf import settings


def generate_id_token(fi_session):
    iss: str = f"{settings.PUBLIC_API_URL}/api/v1/fi/"
    if settings.PUBLIC_FC_PROXY:
        iss = f"{settings.PUBLIC_FC_PROXY}api/v1/fi/"
    return {
        "aud": settings.FI_CLIENT_ID,
        "exp": int(time.time()) + settings.FI_SESSION_AGE,
        "iat": int(time.time()),
        "iss": iss,
        "sub": fi_session.user_data["sub"],
        "nonce": fi_session.nonce,
        "acr": "eidas1",
    }
