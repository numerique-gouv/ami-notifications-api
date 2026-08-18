import urllib.parse

import jwt
from django.conf import settings

_jwks_client = None


def get_jwks_client():
    global _jwks_client
    if _jwks_client:
        print("return jwks client from cache")
        return _jwks_client
    _jwks_client = jwt.PyJWKClient(
        urllib.parse.urljoin(settings.PUBLIC_FC_BASE_URL, settings.FC_JWKS_ENDPOINT)
    )
    return _jwks_client
