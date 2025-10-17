from typing import Any
from urllib.parse import urlencode

import pytest
from litestar import Litestar
from litestar.testing import TestClient
from pytest_httpx import HTTPXMock

from tests.base import ConnectedTestClient

from .utils import check_url_when_logged_out


async def test_rvo_login_callback(
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
        url="https://fcp-low.sbx.dev-franceconnect.fr/api/v2/token",
        json=fake_token_json_response,
    )
    httpx_mock.add_response(
        method="GET", url="https://fcp-low.sbx.dev-franceconnect.fr/api/v2/jwks"
    )
    httpx_mock.add_response(
        method="GET",
        url="https://fcp-low.sbx.dev-franceconnect.fr/api/v2/userinfo",
        json=userinfo,
    )

    def fake_jwt_decode(*args: Any, **params: Any):
        return userinfo

    monkeypatch.setattr("jwt.decode", fake_jwt_decode)

    response = test_client.get("/rvo/login-callback?code=fake-code")

    assert response.request.url == "http://testserver.local/rvo"
    assert test_client.get_session_data() == {
        "id_token": "fake id token",
        "userinfo": userinfo,
    }


async def test_rvo_logout(
    connected_test_client: ConnectedTestClient,
) -> None:
    data: dict[str, str] = {
        "id_token_hint": "fake id token",
        "state": "https://localhost:8000/rvo/logged_out",
        "post_logout_redirect_uri": "https://ami-fc-proxy-dev.osc-fr1.scalingo.io/",
    }
    params: str = urlencode(data)
    url: str = f"https://fcp-low.sbx.dev-franceconnect.fr/api/v2/session/end?{params}"

    response = connected_test_client.get("/rvo/logout", follow_redirects=False)
    assert response.status_code == 302
    assert response.headers["location"] == url
    # Session has been removed, previously to redirecting to FC logout URL.
    assert connected_test_client.get_session_data() == {}


async def test_rvo_home_when_logged_in(
    connected_test_client: ConnectedTestClient,
) -> None:
    response = connected_test_client.get("/rvo", follow_redirects=False)
    assert response.status_code == 200
    assert "/rvo/detail/1" in response.text
    assert "/rvo/detail/2" in response.text


async def test_rvo_detail_when_logged_in(
    connected_test_client: ConnectedTestClient,
) -> None:
    response = connected_test_client.get("/rvo/detail/1", follow_redirects=False)
    assert "Rendez-vous dans votre Agence France Travail Paris 18e Ney" in response.text
    assert response.status_code == 200
    assert "Annuler le RDV" in response.text

    response = connected_test_client.get("/rvo/detail/2", follow_redirects=False)
    assert "Rendez-vous dans votre Maison France Services" in response.text
    assert response.status_code == 200
    assert "Annuler le RDV" in response.text


async def test_rvo_detail_when_logged_out(
    test_client: TestClient[Litestar],
) -> None:
    await check_url_when_logged_out("/rvo/detail/1", test_client)
