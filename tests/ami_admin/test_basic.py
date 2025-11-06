from typing import Any
from urllib.parse import urlencode

import pytest
from litestar import Litestar
from litestar.testing import TestClient
from pytest_httpx import HTTPXMock

from tests.base import ConnectedTestClient


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


async def test_ami_admin_logout(
    connected_test_client: ConnectedTestClient,
) -> None:
    data: dict[str, str] = {
        "id_token_hint": "fake id token",
        "state": "state-not-implemented-yet-and-has-more-than-32-chars",
        "post_logout_redirect_uri": "https://localhost:8000/ami_admin/logout-callback/",
    }
    params: str = urlencode(data)
    url: str = f"https://fca.integ01.dev-agentconnect.fr/api/v2/session/end?{params}"

    response = connected_test_client.get("/ami_admin/logout", follow_redirects=False)
    assert response.status_code == 302
    assert response.headers["location"] == url
    # Session data is still present, so if logging out from FC failed, the user can try again.
    assert connected_test_client.get_session_data() == {
        "id_token": "fake id token",
        "userinfo": connected_test_client.userinfo,
    }


async def test_ami_admin_logout_callback(
    connected_test_client: ConnectedTestClient,
) -> None:
    response = connected_test_client.get(
        "/ami_admin/logout-callback?state=fake-state", follow_redirects=False
    )
    assert response.status_code == 302
    # As the user was properly logged out from FC, the local session is now emptied, and the user redirected to the fake service provider.
    assert response.headers["location"] == "/ami_admin/logged_out"
    assert connected_test_client.get_session_data() == {}
