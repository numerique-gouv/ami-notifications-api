from typing import Any

import pytest


@pytest.fixture
def decoded_id_token() -> dict[str, Any]:
    return {
        "sub": "cff67ebe00792a2f2b5115dcc1a65d115adb3b73653fb3ed1b88ea11a7a2589av1",
        "auth_time": 1763455959,
        "acr": "eidas1",
        "nonce": "YTc3NzZlNjUtNmY3OC00YzExLThmODItMTg0MDg2ZjQ0YzEyLTIwMjUtMTEtMTggMDg6NTI6MzUuNjM1OTYyKzAwOjAw",
        "aud": "33fe498cc172fe691778912a2967baa650b24f1ae0ebbe47ae552f37b2d25ead",
        "exp": 1763456019,
        "iat": 1763455959,
        "iss": "https://fcp-low.sbx.dev-franceconnect.fr/api/v2",
    }
