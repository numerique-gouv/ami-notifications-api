import datetime
import urllib.parse
from typing import Any

import jwt
import pytest
from pytest_httpx import HTTPXMock

from ami.authentication.models import DataNonce, Nonce
from ami.tests.utils import login
from ami.user.models import User
from ami.user.utils import build_fc_hash

API_PART_RESPONSE = {
    "data": {
        "allocataires": [
            {
                "nom_naissance": "TROIS-DUPRE",
                "nom_usage": "DUBOIS",
                "prenoms": "MELISSANDRE JULIETTE",
                "date_naissance": "1981-07-27",
                "sexe": "F",
            },
            {
                "nom_naissance": "DUBOIS",
                "nom_usage": None,
                "prenoms": "PAUL",
                "date_naissance": "1963-10-12",
                "sexe": "M",
            },
        ],
        "enfants": [
            {
                "nom_naissance": "DUBOIS",
                "nom_usage": None,
                "prenoms": "PIERRE",
                "date_naissance": "2004-01-10",
                "sexe": "M",
            },
            {
                "nom_naissance": "DUBOIS",
                "nom_usage": None,
                "prenoms": "LOU",
                "date_naissance": "2015-03-15",
                "sexe": "F",
            },
            {
                "nom_naissance": "DUBOIS",
                "nom_usage": None,
                "prenoms": "HENRY",
                "date_naissance": "2022-06-20",
                "sexe": "M",
            },
        ],
        "adresse": {
            "destinataire": "Monsieur DUBOIS PAUL",
            "complement_information": None,
            "complement_information_geographique": None,
            "numero_libelle_voie": "1 RUE MONTORGUEIL",
            "lieu_dit": None,
            "code_postal_ville": "75002 PARIS",
            "pays": "FRANCE",
        },
        "quotient_familial": {
            "fournisseur": "CNAF",
            "valeur": 2550,
            "annee": 2024,
            "mois": 2,
            "annee_calcul": 2024,
            "mois_calcul": 12,
        },
    },
    "links": {},
    "meta": {},
}


@pytest.mark.parametrize("login_mode", ["relogin", "silent-ami-fi"])
@pytest.mark.django_db
def test_login_for_foyer_data(
    login_mode,
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
            "idp": login_mode,
            "data-mode": "foyer",
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

    if login_mode == "relogin":
        auth = {"authorization": "Bearer fake access token"}
        fake_userinfo_token = "fake userinfo jwt token"
        httpx_mock.add_response(
            method="GET",
            url="https://fcp-low.sbx.dev-franceconnect.fr/api/v2/userinfo",
            match_headers=auth,
            text=fake_userinfo_token,
        )

    auth = {"authorization": "Bearer fake access token"}
    httpx_mock.add_response(
        method="GET",
        url="https://staging.particulier.api.gouv.fr/v3/dss/quotient_familial/france_connect?recipient=13002526500013",
        match_headers=auth,
        json=API_PART_RESPONSE,
    )

    response = app.get(f"/login-callback?code=fake-code&state={nonce.id}")

    assert response.status_code == 302
    redirected_url = response.headers["location"]
    assert redirected_url.startswith("https://localhost:5173/")
    assert redirected_url.endswith("#/login-callback")
    parsed_qs = dict(urllib.parse.parse_qsl(urllib.parse.urlparse(redirected_url).query))
    assert parsed_qs["redirect_to_hash"] == "/profile/foyer"
    data_nonce = parsed_qs["data-nonce"]

    response = app.get(f"/api/v1/users/login-data?nonce={data_nonce}")
    response_data = response.json["foyer"]
    response_data.pop("timestamp")
    assert response_data == {
        "adresse": {
            "code_postal_ville": "75002 PARIS",
            "complement_information": None,
            "complement_information_geographique": None,
            "destinataire": "Monsieur DUBOIS PAUL",
            "lieu_dit": None,
            "numero_libelle_voie": "1 RUE MONTORGUEIL",
            "pays": "FRANCE",
        },
        "allocataires": [
            {
                "date_naissance": "1981-07-27",
                "nom_naissance": "TROIS-DUPRE",
                "nom_usage": "DUBOIS",
                "prenoms": "MELISSANDRE JULIETTE",
                "sexe": "F",
            },
            {
                "date_naissance": "1963-10-12",
                "nom_naissance": "DUBOIS",
                "nom_usage": None,
                "prenoms": "PAUL",
                "sexe": "M",
            },
        ],
        "enfants": [
            {
                "date_naissance": "2004-01-10",
                "nom_naissance": "DUBOIS",
                "nom_usage": None,
                "prenoms": "PIERRE",
                "sexe": "M",
            },
            {
                "date_naissance": "2015-03-15",
                "nom_naissance": "DUBOIS",
                "nom_usage": None,
                "prenoms": "LOU",
                "sexe": "F",
            },
            {
                "date_naissance": "2022-06-20",
                "nom_naissance": "DUBOIS",
                "nom_usage": None,
                "prenoms": "HENRY",
                "sexe": "M",
            },
        ],
        "quotient_familial": {
            "annee": 2024,
            "annee_calcul": 2024,
            "fournisseur": "CAF",
            "mois": 2,
            "mois_calcul": 12,
            "valeur": 2550,
        },
    }
    assert Nonce.objects.count() == 0
    assert DataNonce.objects.count() == 0


@pytest.mark.parametrize("fc_mode", ["noproxy", "proxy"])
@pytest.mark.django_db
def test_relogin_for_foyer_data_login_callback_different_user(
    fc_mode,
    settings,
    app,
    httpx_mock: HTTPXMock,
    monkeypatch: pytest.MonkeyPatch,
    userinfo: dict[str, Any],
    decoded_id_token: dict[str, Any],
    user: User,
) -> None:
    login(app, user)

    if fc_mode == "noproxy":
        settings.PUBLIC_FC_PROXY_BASE_URL = ""
    else:
        settings.PUBLIC_FC_PROXY_BASE_URL = "https://fake-fc-proxy"

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
            "data-mode": "foyer",
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

    auth = {"authorization": "Bearer fake access token"}
    httpx_mock.add_response(
        method="GET",
        url="https://staging.particulier.api.gouv.fr/v3/dss/quotient_familial/france_connect?recipient=13002526500013",
        match_headers=auth,
        json=API_PART_RESPONSE,
    )

    response = app.get(f"/login-callback?code=fake-code&state={nonce.id}")
    assert response.status_code == 302
    # check no new user were created
    assert User.objects.count() == 1
    # check no data nonce has been persisted
    assert DataNonce.objects.count() == 0
    # check redirection is a logout from FranceConnect
    redirected_url = response.headers["location"]
    parsed = urllib.parse.urlparse(redirected_url)
    assert parsed.path == "/api/v2/session/end"
