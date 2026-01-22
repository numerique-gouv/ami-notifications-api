import json
from base64 import urlsafe_b64encode
from typing import Any

import pytest
from litestar import Litestar
from litestar.testing import TestClient
from pytest_httpx import HTTPXMock
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Nonce
from tests.utils import url_contains_param


async def test_login_callback_address(
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
        is_reusable=True,
    )

    auth = {"authorization": "Bearer fake access token"}
    fake_userinfo_token = "fake userinfo jwt token"
    httpx_mock.add_response(
        method="GET",
        url="https://fcp-low.sbx.dev-franceconnect.fr/api/v2/userinfo",
        match_headers=auth,
        text=fake_userinfo_token,
        is_reusable=True,
    )

    address = {
        "numero_libelle_voie": "1 RUE MONTORGUEIL",
        "lieu_dit": "",
        "code_postal_ville": "75002 PARIS",
        "pays": "FRANCE",
    }
    fake_quotient_data = {"data": {"adresse": address}}
    encoded_address = urlsafe_b64encode(json.dumps(address).encode("utf8")).decode("utf8")
    httpx_mock.add_response(
        method="GET",
        url="https://staging.particulier.api.gouv.fr/v3/dss/quotient_familial/france_connect?recipient=13002526500013",
        match_headers=auth,
        json=fake_quotient_data,
    )

    response = test_client.get(
        f"/login-callback?code=fake-code&state={nonce.id}", follow_redirects=False
    )

    assert response.status_code == 302
    redirected_url = response.headers["location"]
    assert redirected_url.startswith("https://localhost:5173")
    assert url_contains_param(
        "address",
        encoded_address,
        redirected_url,
    )

    nonce = Nonce(nonce=NONCE)
    db_session.add(nonce)
    await db_session.commit()
    address = {
        "numero_libelle_voie": "",
        "lieu_dit": "",
        "code_postal_ville": "",
        "pays": "",
    }
    fake_quotient_data = {"data": {"adresse": address}}
    encoded_address = urlsafe_b64encode(json.dumps(address).encode("utf8")).decode("utf8")
    httpx_mock.add_response(
        method="GET",
        url="https://staging.particulier.api.gouv.fr/v3/dss/quotient_familial/france_connect?recipient=13002526500013",
        match_headers=auth,
        json=fake_quotient_data,
    )

    response = test_client.get(
        f"/login-callback?code=fake-code&state={nonce.id}", follow_redirects=False
    )

    assert response.status_code == 302
    redirected_url = response.headers["location"]
    assert redirected_url.startswith("https://localhost:5173")
    assert url_contains_param(
        "address",
        encoded_address,
        redirected_url,
    )


async def test_login_callback_address_no_data(
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
        is_reusable=True,
    )

    auth = {"authorization": "Bearer fake access token"}
    fake_userinfo_token = "fake userinfo jwt token"
    httpx_mock.add_response(
        method="GET",
        url="https://fcp-low.sbx.dev-franceconnect.fr/api/v2/userinfo",
        match_headers=auth,
        text=fake_userinfo_token,
        is_reusable=True,
    )

    fake_quotient_datas: list[dict[str, Any]] = [
        {},
        {"data": {}},
        {"data": {"address": {}}},
    ]
    for fake_quotient_data in fake_quotient_datas:
        nonce = Nonce(nonce=NONCE)
        db_session.add(nonce)
        await db_session.commit()

        httpx_mock.add_response(
            method="GET",
            url="https://staging.particulier.api.gouv.fr/v3/dss/quotient_familial/france_connect?recipient=13002526500013",
            match_headers=auth,
            json=fake_quotient_data,
        )

        response = test_client.get(
            f"/login-callback?code=fake-code&state={nonce.id}", follow_redirects=False
        )

        assert response.status_code == 302
        redirected_url = response.headers["location"]
        assert redirected_url.startswith("https://localhost:5173")
        assert "address" not in redirected_url
