from typing import Any

import pytest
from litestar import Litestar
from litestar.testing import TestClient
from pytest_httpx import HTTPXMock


async def test_ami_admin_login_callback(
    test_client: TestClient[Litestar],
    httpx_mock: HTTPXMock,
    monkeypatch: pytest.MonkeyPatch,
    userinfo: dict[str, Any],
) -> None:
    fake_token_json_response = {
        "access_token": "fake access token",
        "expires_in": 60,
        "id_token": "fake id token",
        "scope": "openid given_name family_name preferred_username birthdate gender birthplace birthcountry email",
        "token_type": "Bearer",
    }
    httpx_mock.add_response(
        method="POST",
        url="https://fca.integ01.dev-agentconnect.fr/api/v2/token",
        json=fake_token_json_response,
    )
    httpx_mock.add_response(method="GET", url="https://fca.integ01.dev-agentconnect.fr/api/v2/jwks")
    httpx_mock.add_response(
        method="GET",
        url="https://fca.integ01.dev-agentconnect.fr/api/v2/userinfo",
        json=userinfo,
    )

    def fake_jwt_decode(*args: Any, **params: Any):
        return userinfo

    monkeypatch.setattr("jwt.decode", fake_jwt_decode)

    response = test_client.get("/ami_admin/login-callback?code=fake-code&state=fake-state")

    assert response.request.url == "http://testserver.local/ami_admin"
    assert test_client.get_session_data() == {
        "id_token": "fake id token",
        "userinfo": userinfo,
    }
