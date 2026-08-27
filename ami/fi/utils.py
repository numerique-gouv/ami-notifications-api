import base64
import math
import time

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ec import EllipticCurvePublicKey
from django.conf import settings


def generate_id_token(fi_session):
    iss: str = f"{settings.PUBLIC_APP_URL}/api/v1/fi/"
    if settings.PUBLIC_FC_PROXY_BASE_URL:
        iss = f"{settings.PUBLIC_FC_PROXY_BASE_URL}/api/v1/fi/"
    return {
        "aud": settings.FI_CLIENT_ID,
        "exp": int(time.time()) + settings.FI_SESSION_AGE,
        "iat": int(time.time()),
        "iss": iss,
        "sub": fi_session.user_data["sub"],
        "nonce": fi_session.nonce,
        "acr": "eidas1",
    }


def encode_b64url_int(data: int) -> str:
    length = max(data.bit_length(), 8)
    length = math.ceil(length / 8)
    return (
        base64.urlsafe_b64encode(data.to_bytes(byteorder="big", length=length))
        .rstrip(b"=")
        .decode("ascii")
    )


def generate_jwk(pem_public_key, kid):
    public_key = serialization.load_pem_public_key(pem_public_key, backend=default_backend())
    if not isinstance(public_key, EllipticCurvePublicKey):
        raise ValueError("Expected Elliptic Curve public key")
    numbers = public_key.public_numbers()
    return {
        "kty": "EC",
        "use": "sig",
        "kid": kid,
        "alg": "ES256",
        "crv": "P-256",
        "x": encode_b64url_int(numbers.x),
        "y": encode_b64url_int(numbers.y),  # type: ignore
    }
