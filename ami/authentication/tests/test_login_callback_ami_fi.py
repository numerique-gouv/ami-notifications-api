import json
from base64 import urlsafe_b64encode
from typing import Any

import jwt
import pytest
from pytest_httpx import HTTPXMock

from ami.authentication.models import Nonce
from ami.tests.utils import url_contains_param
from ami.user.models import User


@pytest.mark.django_db
def test_login_callback_ami_fi(
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
    settings.API_PARTICULIER_STATUT_ETUDIANT_ENABLED = True

    NONCE = decoded_id_token["nonce"]
    nonce = Nonce.objects.create(
        nonce=NONCE,
        context={
            "idp": "ami-fi",
            "provider_ids": ["api_particulier_quotient", "api_particulier_statut_etudiant"],
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

    auth = {"authorization": "Bearer fake access token"}
    fake_userinfo_token = "fake userinfo jwt token"
    httpx_mock.add_response(
        method="GET",
        url="https://fcp-low.sbx.dev-franceconnect.fr/api/v2/userinfo",
        match_headers=auth,
        text=fake_userinfo_token,
    )

    address = {
        "numero_libelle_voie": "1 RUE MONTORGUEIL",
        "lieu_dit": "",
        "code_postal_ville": "75002 PARIS",
        "pays": "FRANCE",
    }
    fake_quotient_data = {"data": {"adresse": address}}
    encoded_address = urlsafe_b64encode(json.dumps(fake_quotient_data).encode()).decode()
    httpx_mock.add_response(
        method="GET",
        url="https://staging.particulier.api.gouv.fr/v3/dss/quotient_familial/france_connect?recipient=13002526500013",
        match_headers=auth,
        json=fake_quotient_data,
    )

    statut = {
        "admissions": [
            {
                "date_debut": "2022-09-01",
                "date_fin": "2023-08-31",
                "est_inscrit": True,
                "regime_formation": {"libelle": "formation initiale", "code": "RF1"},
                "code_cog_insee_commune": "29085",
                "etablissement_etudes": {
                    "uai": "0011402U",
                    "nom": "EGC AIN BOURG EN BRESSE EC GESTION ET COMMERCE (01000)",
                },
            }
        ]
    }
    fake_statut_data = {"data": statut}
    encoded_statut = urlsafe_b64encode(json.dumps(fake_statut_data).encode()).decode()
    httpx_mock.add_response(
        method="GET",
        url="https://staging.particulier.api.gouv.fr/v3/mesri/statut_etudiant/france_connect?recipient=13002526500013",
        match_headers=auth,
        json=fake_statut_data,
    )

    response = app.get(f"/login-callback?code=fake-code&state={nonce.id}")

    assert response.status_code == 302
    redirected_url = response.headers["location"]
    assert redirected_url.startswith("https://localhost:5173/")
    assert redirected_url.endswith("#/fi")
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
        "id_token",
        "fake id token",
        redirected_url,
    )
    assert url_contains_param(
        "is_logged_in",
        "true",
        redirected_url,
    )
    assert url_contains_param(
        "api_particulier_quotient",
        encoded_address,
        redirected_url,
    )
    assert url_contains_param(
        "api_particulier_statut_etudiant",
        encoded_statut,
        redirected_url,
    )

    assert Nonce.objects.count() == 0

    assert User.objects.count() == 1
    user = User.objects.get()

    assert user.fc_hash == "4abd71ec1f581dce2ea2221cbeac7c973c6aea7bcb835acdfe7d6494f1528060"
    assert user.last_logged_in is not None


@pytest.mark.django_db
def test_login_callback_ami_fi_no_quotient(
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
    settings.API_PARTICULIER_STATUT_ETUDIANT_ENABLED = True
    settings.API_PARTICULIER_QUOTIENT_ENABLED = False

    NONCE = decoded_id_token["nonce"]
    nonce = Nonce.objects.create(
        nonce=NONCE,
        context={
            "idp": "ami-fi",
            "provider_ids": ["api_particulier_quotient"],
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
    assert redirected_url.endswith("#/fi")
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
        "id_token",
        "fake id token",
        redirected_url,
    )
    assert url_contains_param(
        "is_logged_in",
        "true",
        redirected_url,
    )
    assert "api_particulier_quotient" not in redirected_url
    assert "api_particulier_statut_etudiant" not in redirected_url

    assert Nonce.objects.count() == 0

    assert User.objects.count() == 1
    user = User.objects.get()

    assert user.fc_hash == "4abd71ec1f581dce2ea2221cbeac7c973c6aea7bcb835acdfe7d6494f1528060"
    assert user.last_logged_in is not None


@pytest.mark.django_db
def test_login_callback_ami_fi_no_statut_edudiant(
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
    settings.API_PARTICULIER_STATUT_ETUDIANT_ENABLED = False

    NONCE = decoded_id_token["nonce"]
    nonce = Nonce.objects.create(
        nonce=NONCE,
        context={
            "idp": "ami-fi",
            "provider_ids": ["api_particulier_statut_etudiant"],
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
    assert redirected_url.endswith("#/fi")
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
        "id_token",
        "fake id token",
        redirected_url,
    )
    assert url_contains_param(
        "is_logged_in",
        "true",
        redirected_url,
    )
    assert "api_particulier_quotient" not in redirected_url
    assert "api_particulier_statut_etudiant" not in redirected_url

    assert Nonce.objects.count() == 0

    assert User.objects.count() == 1
    user = User.objects.get()

    assert user.fc_hash == "4abd71ec1f581dce2ea2221cbeac7c973c6aea7bcb835acdfe7d6494f1528060"
    assert user.last_logged_in is not None
