from typing import Any

import pytest
from litestar import Litestar
from litestar.testing import TestClient
from pytest_httpx import HTTPXMock
from sqlalchemy.ext.asyncio import AsyncSession

from app import env
from app.models import Nonce
from tests.utils import url_contains_param


async def test_login_callback_token_query_failure(
    test_client: TestClient[Litestar],
    db_session: AsyncSession,
    httpx_mock: HTTPXMock,
) -> None:
    NONCE = "some random nonce"
    nonce = Nonce(nonce=NONCE)
    db_session.add(nonce)
    await db_session.commit()

    token_failure_response = {
        "error": "invalid_grant",
        "error_description": " grant request is invalid (authorization code not found)",
        "error_uri": "https://docs.partenaires.franceconnect.gouv.fr/fs/fs-technique/fs-technique-erreurs/"
        "?code=Y049E20B&id=801d508c-72d7-459d-8947-104cf89ce015",
    }
    httpx_mock.add_response(
        method="POST",
        url="https://fcp-low.sbx.dev-franceconnect.fr/api/v2/token",
        json=token_failure_response,
        status_code=401,
    )

    response = test_client.get(
        f"/login-callback?code=fake-code&state={nonce.id}", follow_redirects=False
    )

    assert response.status_code == 302
    redirected_url = response.headers["location"]
    assert (
        redirected_url
        == "https://localhost:5173/?error=Erreur+lors+de+la+FranceConnexion%2C+veuillez+r%C3%A9essayer+plus+tard.&error_type=FranceConnect"
    )


async def test_login_callback_userinfo_query_failure(
    test_client: TestClient[Litestar],
    db_session: AsyncSession,
    httpx_mock: HTTPXMock,
    monkeypatch: pytest.MonkeyPatch,
    decoded_id_token: dict[str, Any],
) -> None:
    def fake_jwt_decode(*args: Any, **params: Any):
        return decoded_id_token

    monkeypatch.setattr("jwt.decode", fake_jwt_decode)
    monkeypatch.setattr("app.controllers.auth.env.FC_AMI_CLIENT_SECRET", "fake-client-secret")
    monkeypatch.setattr(
        "app.controllers.auth.env.PUBLIC_FC_SCOPE",
        env.PUBLIC_FC_SCOPE.replace(" cnaf_quotient_familial", ""),
    )

    NONCE = decoded_id_token["nonce"]
    nonce = Nonce(nonce=NONCE)
    db_session.add(nonce)
    await db_session.commit()

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

    auth = {"authorization": "Bearer fake access token"}
    httpx_mock.add_response(
        method="GET",
        url="https://fcp-low.sbx.dev-franceconnect.fr/api/v2/userinfo",
        match_headers=auth,
        status_code=500,
    )

    response = test_client.get(
        f"/login-callback?code=fake-code&state={nonce.id}", follow_redirects=False
    )

    assert response.status_code == 302
    redirected_url = response.headers["location"]
    assert (
        redirected_url
        == "https://localhost:5173/?error=Erreur+lors+de+la+FranceConnexion%2C+veuillez+r%C3%A9essayer+plus+tard.&error_type=FranceConnect"
    )


async def test_login_callback_address_query_failure(
    test_client: TestClient[Litestar],
    db_session: AsyncSession,
    httpx_mock: HTTPXMock,
    monkeypatch: pytest.MonkeyPatch,
    userinfo: dict[str, Any],
    decoded_id_token: dict[str, Any],
) -> None:
    def fake_jwt_decode(*args: Any, **params: Any):
        encoded = args[0]
        if encoded == "fake id token":
            return decoded_id_token
        return userinfo

    monkeypatch.setattr("jwt.decode", fake_jwt_decode)
    monkeypatch.setattr("app.controllers.auth.env.FC_AMI_CLIENT_SECRET", "fake-client-secret")

    NONCE = decoded_id_token["nonce"]
    nonce = Nonce(nonce=NONCE)
    db_session.add(nonce)
    await db_session.commit()

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

    auth = {"authorization": "Bearer fake access token"}
    fake_userinfo_token = "fake userinfo jwt token"
    httpx_mock.add_response(
        method="GET",
        url="https://fcp-low.sbx.dev-franceconnect.fr/api/v2/userinfo",
        match_headers=auth,
        text=fake_userinfo_token,
    )

    httpx_mock.add_response(
        method="GET",
        url="https://staging.particulier.api.gouv.fr/v3/dss/quotient_familial/france_connect?recipient=13002526500013",
        match_headers=auth,
        status_code=500,
    )

    response = test_client.get(
        f"/login-callback?code=fake-code&state={nonce.id}", follow_redirects=False
    )

    assert response.status_code == 302
    redirected_url = response.headers["location"]
    assert redirected_url.startswith("https://localhost:5173")
    assert "address" not in redirected_url


async def test_login_callback_fc_error(
    test_client: TestClient[Litestar],
) -> None:
    response = test_client.get(
        "/login-callback?error=access_denied&error_description=User+auth+aborted&state=some-state",
        follow_redirects=False,
    )

    assert response.status_code == 302
    redirected_url = response.headers["location"]
    assert url_contains_param("error_type", "FranceConnect", redirected_url)
    assert url_contains_param("error", "access_denied", redirected_url)
    assert url_contains_param("error_description", "User auth aborted", redirected_url)
    assert url_contains_param("code", "fc_error", redirected_url)


async def test_login_callback_error(
    test_client: TestClient[Litestar],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_retry():
        raise Exception()

    monkeypatch.setattr("app.controllers.auth.retry_fc_later", fake_retry)
    response = test_client.get("/login-callback?state=some-state", follow_redirects=False)
    redirected_url = response.headers["location"]
    assert redirected_url == "https://localhost:5173/#/technical-error"
