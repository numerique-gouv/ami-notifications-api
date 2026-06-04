from typing import Any

import jwt
import pytest
from pytest_httpx import HTTPXMock

from ami.authentication.models import Nonce
from ami.tests.utils import url_contains_param


@pytest.mark.django_db
def test_login_callback_silent_ami_fi(
    settings,
    app,
    httpx_mock: HTTPXMock,
    monkeypatch: pytest.MonkeyPatch,
    userinfo: dict[str, Any],
    decoded_id_token: dict[str, Any],
) -> None:
    original_jwt_decode = jwt.decode

    def fake_jwt_decode(*args: Any, **params: Any):
        encoded = args[0]
        if encoded == "fake id token":
            return decoded_id_token
        return original_jwt_decode(*args, **params)

    monkeypatch.setattr("jwt.decode", fake_jwt_decode)
    settings.FC_AMI_CLIENT_SECRET = "fake-client-secret"

    NONCE = decoded_id_token["nonce"]
    nonce = Nonce.objects.create(
        nonce=NONCE,
        context={
            "idp": "silent-ami-fi",
            "redirect_url": "",
        },
    )

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

    response = app.get(f"/login-callback?code=fake-code&state={nonce.id}")

    assert response.status_code == 302
    redirected_url = response.headers["location"]
    assert redirected_url.startswith("https://localhost:5173/")
    assert redirected_url.endswith("#/silent-login")
    assert url_contains_param(
        "is_logged_in",
        "true",
        redirected_url,
    )
    assert url_contains_param(
        "id_token",
        "fake id token",
        redirected_url,
    )
    assert url_contains_param(
        "redirect_url",
        "",
        redirected_url,
    )
    assert "&redirect_url=#/silent-login" in redirected_url
    assert "user_data" not in redirected_url
    assert "user_first_login" not in redirected_url
    assert "user_fc_hash" not in redirected_url
    assert "address" not in redirected_url
    assert "api_particulier_quotient" not in redirected_url
    assert "api_particulier_statut_etudiant" not in redirected_url

    assert Nonce.objects.count() == 0


@pytest.mark.django_db
def test_login_callback_silent_ami_fi_with_redirect_url(
    settings,
    app,
    httpx_mock: HTTPXMock,
    monkeypatch: pytest.MonkeyPatch,
    userinfo: dict[str, Any],
    decoded_id_token: dict[str, Any],
) -> None:
    original_jwt_decode = jwt.decode

    def fake_jwt_decode(*args: Any, **params: Any):
        encoded = args[0]
        if encoded == "fake id token":
            return decoded_id_token
        return original_jwt_decode(*args, **params)

    monkeypatch.setattr("jwt.decode", fake_jwt_decode)
    settings.FC_AMI_CLIENT_SECRET = "fake-client-secret"

    NONCE = decoded_id_token["nonce"]
    nonce = Nonce.objects.create(
        nonce=NONCE,
        context={
            "idp": "silent-ami-fi",
            "redirect_url": "http://foo?bar",
        },
    )

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

    response = app.get(f"/login-callback?code=fake-code&state={nonce.id}")

    assert response.status_code == 302
    redirected_url = response.headers["location"]
    assert redirected_url.startswith("https://localhost:5173/")
    assert redirected_url.endswith("#/silent-login")
    assert url_contains_param(
        "is_logged_in",
        "true",
        redirected_url,
    )
    assert url_contains_param(
        "id_token",
        "fake id token",
        redirected_url,
    )
    assert url_contains_param(
        "redirect_url",
        "http://foo?bar",
        redirected_url,
    )
    assert "user_data" not in redirected_url
    assert "user_first_login" not in redirected_url
    assert "user_fc_hash" not in redirected_url
    assert "address" not in redirected_url
    assert "api_particulier_quotient" not in redirected_url
    assert "api_particulier_statut_etudiant" not in redirected_url

    assert Nonce.objects.count() == 0
