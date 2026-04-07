import time

from django.conf import settings


def generate_id_token(fi_session):
    return {
        "aud": settings.FC_AMI_CLIENT_ID,
        "exp": int(time.time()) + settings.FI_SESSION_AGE,
        "iat": int(time.time()),
        "iss": settings.FI_ISS,
        "sub": fi_session.user_data["sub"],
        "nonce": fi_session.nonce,
        "acr": "eidas1",
    }
