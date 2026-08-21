import datetime
import urllib.parse
from typing import Any

import jwt
import pytest
from pytest_httpx import HTTPXMock

from ami.authentication.models import Nonce
from ami.tests.utils import login, url_contains_param
from ami.user.models import User
from ami.user.utils import build_fc_hash


@pytest.mark.django_db
def test_relogin_france_connect_login_callback(
    settings,
    app,
    httpx_mock: HTTPXMock,
    monkeypatch: pytest.MonkeyPatch,
    userinfo: dict[str, Any],
    decoded_id_token: dict[str, Any],
) -> None:
    fc_hash = build_fc_hash(
        given_name=userinfo["given_name"],
        family_name=userinfo["family_name"],
        birthdate=userinfo["birthdate"],
        gender=userinfo["gender"],
        birthplace=userinfo["birthplace"],
        birthcountry=userinfo["birthcountry"],
    )
    user = User.objects.create(
        fc_hash=fc_hash, last_logged_in=datetime.datetime.now(datetime.timezone.utc)
    )
    login(app, user)

    original_jwt_decode = jwt.decode

    def fake_jwt_decode(*args: Any, **params: Any):
        encoded = args[0]
        if encoded == "fake id token":
            return decoded_id_token
        if encoded == "fake userinfo jwt token":
            return userinfo
        return original_jwt_decode(*args, **params)

    monkeypatch.setattr("jwt.decode", fake_jwt_decode)
    settings.FC_AMI_CLIENT_SECRET = "fake-client-secret"

    NONCE = decoded_id_token["nonce"]
    nonce = Nonce.objects.create(
        nonce=NONCE,
        context={
            "idp": "relogin",
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
        is_reusable=True,
    )

    auth = {"authorization": "Bearer fake access token"}
    fake_userinfo_token = "fake userinfo jwt token"
    httpx_mock.add_response(
        method="GET",
        url="https://fcp-low.sbx.dev-franceconnect.fr/api/v2/userinfo",
        match_headers=auth,
        text=fake_userinfo_token,
    )

    response = app.get(f"/login-callback?code=fake-code&state={nonce.id}")

    assert response.status_code == 302
    redirected_url = response.headers["location"]
    assert redirected_url.startswith("https://localhost:5173/")
    assert redirected_url.endswith("#/login-callback")
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
    assert "?login_redirect_url=&id_token=fake+id+token#/login-callback" in redirected_url
    assert "user_data" not in redirected_url
    assert "user_first_login" not in redirected_url
    assert "user_fc_hash" not in redirected_url
    assert "address" not in redirected_url
    assert "api_particulier_quotient" not in redirected_url

    assert Nonce.objects.count() == 0


@pytest.mark.django_db
def test_relogin_france_connect_login_callback_not_logged_in(
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
        if encoded == "fake userinfo jwt token":
            return userinfo
        return original_jwt_decode(*args, **params)

    monkeypatch.setattr("jwt.decode", fake_jwt_decode)
    settings.FC_AMI_CLIENT_SECRET = "fake-client-secret"

    NONCE = decoded_id_token["nonce"]
    nonce = Nonce.objects.create(
        nonce=NONCE,
        context={
            "idp": "relogin",
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
        is_reusable=True,
    )

    auth = {"authorization": "Bearer fake access token"}
    fake_userinfo_token = "fake userinfo jwt token"
    httpx_mock.add_response(
        method="GET",
        url="https://fcp-low.sbx.dev-franceconnect.fr/api/v2/userinfo",
        match_headers=auth,
        text=fake_userinfo_token,
    )

    response = app.get(f"/login-callback?code=fake-code&state={nonce.id}")
    assert response.status_code == 302
    redirected_url = response.headers["location"]
    assert redirected_url.startswith("https://localhost:5173/")
    assert redirected_url.endswith("#/technical-error")


@pytest.mark.django_db
def test_relogin_france_connect_login_callback_different_user(
    settings,
    app,
    httpx_mock: HTTPXMock,
    monkeypatch: pytest.MonkeyPatch,
    userinfo: dict[str, Any],
    decoded_id_token: dict[str, Any],
    user: User,
) -> None:
    login(app, user)

    original_jwt_decode = jwt.decode

    def fake_jwt_decode(*args: Any, **params: Any):
        encoded = args[0]
        if encoded == "fake id token":
            return decoded_id_token
        if encoded == "fake userinfo jwt token":
            return userinfo
        return original_jwt_decode(*args, **params)

    monkeypatch.setattr("jwt.decode", fake_jwt_decode)
    settings.FC_AMI_CLIENT_SECRET = "fake-client-secret"

    NONCE = decoded_id_token["nonce"]
    nonce = Nonce.objects.create(
        nonce=NONCE,
        context={
            "idp": "relogin",
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
        is_reusable=True,
    )

    auth = {"authorization": "Bearer fake access token"}
    fake_userinfo_token = "fake userinfo jwt token"
    httpx_mock.add_response(
        method="GET",
        url="https://fcp-low.sbx.dev-franceconnect.fr/api/v2/userinfo",
        match_headers=auth,
        text=fake_userinfo_token,
    )

    response = app.get(f"/login-callback?code=fake-code&state={nonce.id}")
    assert response.status_code == 302
    # check redirection is a logout from FranceConnect
    redirected_url = response.headers["location"]
    assert urllib.parse.urlparse(redirected_url).path == "/api/v2/session/end"

    # with a state sending the user back to the homepage with a "does not match" banner
    assert url_contains_param(
        "state",
        "https://localhost:5173/?user_does_not_match",
        redirected_url,
    )
    assert User.objects.count() == 1  # no user created at login
