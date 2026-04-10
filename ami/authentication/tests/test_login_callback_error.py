from typing import Any

import pytest
from pytest_httpx import HTTPXMock

from ami.authentication.models import Nonce
from ami.tests.utils import url_contains_param


@pytest.mark.django_db
def test_login_callback_token_query_failure(
    django_app,
    httpx_mock: HTTPXMock,
) -> None:
    NONCE = "some random nonce"
    nonce = Nonce.objects.create(nonce=NONCE)

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

    response = django_app.get(f"/login-callback?code=fake-code&state={nonce.id}")

    assert response.status_code == 302
    redirected_url = response.headers["location"]
    assert (
        redirected_url
        == "https://localhost:5173/?error=Erreur+lors+de+la+FranceConnexion%2C+veuillez+r%C3%A9essayer+plus+tard.&error_type=FranceConnect"
    )


@pytest.mark.django_db
def test_login_callback_userinfo_query_failure(
    settings,
    django_app,
    httpx_mock: HTTPXMock,
    monkeypatch: pytest.MonkeyPatch,
    decoded_id_token: dict[str, Any],
) -> None:
    def fake_jwt_decode(*args: Any, **params: Any):
        return decoded_id_token

    monkeypatch.setattr("jwt.decode", fake_jwt_decode)
    settings.FC_AMI_CLIENT_SECRET = "fake-client-secret"
    settings.FC_SCOPE = settings.FC_SCOPE.replace(" cnaf_enfants cnaf_adresse", "")

    NONCE = decoded_id_token["nonce"]
    nonce = Nonce.objects.create(nonce=NONCE)

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

    response = django_app.get(f"/login-callback?code=fake-code&state={nonce.id}")

    assert response.status_code == 302
    redirected_url = response.headers["location"]
    assert (
        redirected_url
        == "https://localhost:5173/?error=Erreur+lors+de+la+FranceConnexion%2C+veuillez+r%C3%A9essayer+plus+tard.&error_type=FranceConnect"
    )


@pytest.mark.django_db
def test_login_callback_address_query_failure_500(
    settings,
    django_app,
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
    settings.FC_AMI_CLIENT_SECRET = "fake-client-secret"

    NONCE = decoded_id_token["nonce"]
    nonce = Nonce.objects.create(nonce=NONCE)

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

    response = django_app.get(f"/login-callback?code=fake-code&state={nonce.id}")

    assert response.status_code == 302
    redirected_url = response.headers["location"]
    assert redirected_url.startswith("https://localhost:5173")
    assert url_contains_param(
        "user_data",
        "fake userinfo jwt token",
        redirected_url,
    )
    assert url_contains_param(
        "user_first_login",
        "true",
        redirected_url,
    )
    assert url_contains_param(
        "user_fc_hash",
        "4abd71ec1f581dce2ea2221cbeac7c973c6aea7bcb835acdfe7d6494f1528060",
        redirected_url,
    )
    assert url_contains_param(
        "is_logged_in",
        "true",
        redirected_url,
    )
    assert "address" not in redirected_url


@pytest.mark.django_db
def test_login_callback_address_query_failure_400(
    settings,
    django_app,
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
    settings.FC_AMI_CLIENT_SECRET = "fake-client-secret"

    NONCE = decoded_id_token["nonce"]
    nonce = Nonce.objects.create(nonce=NONCE)

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
        status_code=400,
        json={"foo": "bar"},
    )

    response = django_app.get(f"/login-callback?code=fake-code&state={nonce.id}")

    assert response.status_code == 302
    redirected_url = response.headers["location"]
    assert redirected_url.startswith("https://localhost:5173")
    assert url_contains_param(
        "user_data",
        "fake userinfo jwt token",
        redirected_url,
    )
    assert url_contains_param(
        "user_first_login",
        "true",
        redirected_url,
    )
    assert url_contains_param(
        "user_fc_hash",
        "4abd71ec1f581dce2ea2221cbeac7c973c6aea7bcb835acdfe7d6494f1528060",
        redirected_url,
    )
    assert url_contains_param(
        "is_logged_in",
        "true",
        redirected_url,
    )
    assert "address" not in redirected_url


def test_login_callback_fc_error(
    django_app,
) -> None:
    response = django_app.get(
        "/login-callback?error=access_denied&error_description=User+auth+aborted&state=some-state"
    )

    assert response.status_code == 302
    redirected_url = response.headers["location"]
    assert url_contains_param("error_type", "FranceConnect", redirected_url)
    assert url_contains_param("error", "access_denied", redirected_url)
    assert url_contains_param("error_description", "User auth aborted", redirected_url)
    assert url_contains_param("code", "fc_error", redirected_url)


def test_login_callback_error(
    django_app,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_retry(*args):
        raise Exception()

    monkeypatch.setattr("ami.authentication.views.retry_fc_later", fake_retry)
    response = django_app.get("/login-callback?state=some-state")
    redirected_url = response.headers["location"]
    assert redirected_url == "https://localhost:5173/technical-error"
