from typing import Any

import jwt
import pytest
from django.utils.timezone import now
from pytest_httpx import HTTPXMock

from ami.authentication.auth import decode_jwt_token
from ami.authentication.models import Nonce
from ami.notification.models import ScheduledNotification
from ami.tests.utils import url_contains_param
from ami.user.models import User
from ami.user.utils import build_fc_hash


@pytest.mark.django_db
def test_login_callback(
    settings,
    django_app,
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
    settings.PUBLIC_FC_SCOPE = settings.PUBLIC_FC_SCOPE.replace(" cnaf_enfants cnaf_adresse", "")

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

    token = decode_jwt_token(
        response.client.cookies[settings.AUTH_COOKIE_JWT_NAME].value.split(" ")[1].replace('"', "")
    )
    assert token
    assert token["jti"] is not None

    assert Nonce.objects.count() == 0

    assert User.objects.count() == 1
    user = User.objects.get()

    assert user.fc_hash == "4abd71ec1f581dce2ea2221cbeac7c973c6aea7bcb835acdfe7d6494f1528060"
    assert user.last_logged_in is not None

    assert ScheduledNotification.objects.count() == 1
    scheduled_notification = ScheduledNotification.objects.get()
    assert scheduled_notification.user == user
    assert scheduled_notification.content_title == "Bienvenue sur AMI 👋"
    assert (
        scheduled_notification.content_body
        == "Ici, vous pourrez gérer votre vie administrative, suivre l'avancement de vos démarches et recevoir des rappels personnalisés."
    )
    assert scheduled_notification.content_icon == "fr-icon-information-line"
    assert scheduled_notification.reference == "ami:welcome"
    assert scheduled_notification.scheduled_at < now()
    assert scheduled_notification.sender == "AMI"
    assert scheduled_notification.sent_at is None


@pytest.mark.django_db
def test_login_callback_user_already_seen(
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
    settings.PUBLIC_FC_SCOPE = settings.PUBLIC_FC_SCOPE.replace(" cnaf_enfants cnaf_adresse", "")

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

    fc_hash = build_fc_hash(
        given_name=userinfo["given_name"],
        family_name=userinfo["family_name"],
        birthdate=userinfo["birthdate"],
        gender=userinfo["gender"],
        birthplace=userinfo["birthplace"],
        birthcountry=userinfo["birthcountry"],
    )
    user = User.objects.create(fc_hash=fc_hash, last_logged_in=now())

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
        "false",
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
    assert Nonce.objects.count() == 0

    assert User.objects.count() == 1
    user = User.objects.get()

    assert user.fc_hash == "4abd71ec1f581dce2ea2221cbeac7c973c6aea7bcb835acdfe7d6494f1528060"
    assert user.last_logged_in is not None

    assert ScheduledNotification.objects.count() == 0


@pytest.mark.django_db
def test_login_callback_user_never_seen(
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
    settings.PUBLIC_FC_SCOPE = settings.PUBLIC_FC_SCOPE.replace(" cnaf_enfants cnaf_adresse", "")

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

    fc_hash = build_fc_hash(
        given_name=userinfo["given_name"],
        family_name=userinfo["family_name"],
        birthdate=userinfo["birthdate"],
        gender=userinfo["gender"],
        birthplace=userinfo["birthplace"],
        birthcountry=userinfo["birthcountry"],
    )
    user = User.objects.create(fc_hash=fc_hash)

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
    assert Nonce.objects.count() == 0

    assert User.objects.count() == 1
    user = User.objects.get()

    assert user.fc_hash == "4abd71ec1f581dce2ea2221cbeac7c973c6aea7bcb835acdfe7d6494f1528060"
    assert user.last_logged_in is not None

    assert ScheduledNotification.objects.count() == 1
    scheduled_notification = ScheduledNotification.objects.get()
    assert scheduled_notification.user == user
    assert scheduled_notification.content_title == "Bienvenue sur AMI 👋"
    assert (
        scheduled_notification.content_body
        == "Ici, vous pourrez gérer votre vie administrative, suivre l'avancement de vos démarches et recevoir des rappels personnalisés."
    )
    assert scheduled_notification.content_icon == "fr-icon-information-line"
    assert scheduled_notification.reference == "ami:welcome"
    assert scheduled_notification.scheduled_at < now()
    assert scheduled_notification.sender == "AMI"
    assert scheduled_notification.sent_at is None


@pytest.mark.django_db
def test_login_callback_bad_state(
    django_app,
) -> None:
    NONCE = "some random nonce"
    Nonce.objects.create(nonce=NONCE)

    response = django_app.get("/login-callback?code=fake-code&state=")
    assert response.status_code == 302
    redirected_url = response.headers["location"]
    assert url_contains_param("error_type", "FranceConnect", redirected_url)
    assert url_contains_param(
        "error", "Erreur lors de la FranceConnexion, veuillez réessayer plus tard.", redirected_url
    )
    assert url_contains_param("code", "missing_state", redirected_url)

    response = django_app.get("/login-callback?code=fake-code&state=some-other-state")
    assert response.status_code == 302
    redirected_url = response.headers["location"]
    assert url_contains_param("error_type", "FranceConnect", redirected_url)
    assert url_contains_param(
        "error", "Erreur lors de la FranceConnexion, veuillez réessayer plus tard.", redirected_url
    )
    assert url_contains_param("code", "invalid_state", redirected_url)

    response = django_app.get("/login-callback?code=fake-code&state={uuid.uuid4()}")
    assert response.status_code == 302
    redirected_url = response.headers["location"]
    assert url_contains_param("error_type", "FranceConnect", redirected_url)
    assert url_contains_param(
        "error", "Erreur lors de la FranceConnexion, veuillez réessayer plus tard.", redirected_url
    )
    assert url_contains_param("code", "invalid_state", redirected_url)


@pytest.mark.django_db
def test_login_callback_bad_id_token(
    django_app,
    httpx_mock: HTTPXMock,
    decoded_id_token: dict[str, Any],
) -> None:
    NONCE = decoded_id_token["nonce"]
    nonce = Nonce.objects.create(nonce=NONCE)

    fake_token_json_response = {
        "access_token": "fake access token",
        "expires_in": 60,
        "scope": "openid given_name family_name preferred_username birthdate gender birthplace birthcountry email",
        "token_type": "Bearer",
    }
    httpx_mock.add_response(
        method="POST",
        url="https://fcp-low.sbx.dev-franceconnect.fr/api/v2/token",
        json=fake_token_json_response,
    )

    response = django_app.get(f"/login-callback?code=fake-code&state={nonce.id}")

    assert response.status_code == 302
    redirected_url = response.headers["location"]
    assert url_contains_param("error_type", "FranceConnect", redirected_url)
    assert url_contains_param(
        "error", "Erreur lors de la FranceConnexion, veuillez réessayer plus tard.", redirected_url
    )
    assert url_contains_param("code", "missing_id_token", redirected_url)


@pytest.mark.django_db
def test_login_callback_bad_nonce(
    settings,
    django_app,
    httpx_mock: HTTPXMock,
    monkeypatch: pytest.MonkeyPatch,
    decoded_id_token: dict[str, Any],
) -> None:
    def fake_jwt_decode(*args: Any, **params: Any):
        return decoded_id_token

    monkeypatch.setattr("jwt.decode", fake_jwt_decode)

    NONCE = "some random nonce"
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
        is_reusable=True,
    )
    settings.FC_AMI_CLIENT_SECRET = "fake-client-secret"

    response = django_app.get(f"/login-callback?code=fake-code&state={nonce.id}")

    assert response.status_code == 302
    redirected_url = response.headers["location"]
    assert url_contains_param("error_type", "FranceConnect", redirected_url)
    assert url_contains_param(
        "error", "Erreur lors de la FranceConnexion, veuillez réessayer plus tard.", redirected_url
    )
    assert url_contains_param("code", "invalid_nonce", redirected_url)
    assert Nonce.objects.count() == 0

    nonce = Nonce.objects.create(nonce=NONCE)
    decoded_id_token.pop("nonce")

    response = django_app.get(f"/login-callback?code=fake-code&state={nonce.id}")

    assert response.status_code == 302
    redirected_url = response.headers["location"]
    assert url_contains_param("error_type", "FranceConnect", redirected_url)
    assert url_contains_param(
        "error", "Erreur lors de la FranceConnexion, veuillez réessayer plus tard.", redirected_url
    )
    assert url_contains_param("code", "missing_nonce", redirected_url)
    assert Nonce.objects.count() == 0


@pytest.mark.django_db
def test_login_callback_bad_token_info(
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

    NONCE = decoded_id_token["nonce"]
    nonce = Nonce.objects.create(nonce=NONCE)

    fake_token_json_response = {
        "access_token": "fake access token",
        "expires_in": 60,
        "id_token": "fake id token",
        "scope": "openid given_name family_name preferred_username birthdate gender birthplace birthcountry email",
    }
    httpx_mock.add_response(
        method="POST",
        url="https://fcp-low.sbx.dev-franceconnect.fr/api/v2/token",
        json=fake_token_json_response,
    )

    response = django_app.get(f"/login-callback?code=fake-code&state={nonce.id}")
    redirected_url = response.headers["location"]
    assert url_contains_param("error_type", "FranceConnect", redirected_url)
    assert url_contains_param(
        "error", "Erreur lors de la FranceConnexion, veuillez réessayer plus tard.", redirected_url
    )
    assert url_contains_param("code", "missing_token_type", redirected_url)
    assert Nonce.objects.count() == 0

    nonce = Nonce.objects.create(nonce=NONCE)

    fake_token_json_response = {
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

    response = django_app.get(f"/login-callback?code=fake-code&state={nonce.id}")
    redirected_url = response.headers["location"]
    assert url_contains_param("error_type", "FranceConnect", redirected_url)
    assert url_contains_param(
        "error", "Erreur lors de la FranceConnexion, veuillez réessayer plus tard.", redirected_url
    )
    assert url_contains_param("code", "missing_access_token", redirected_url)
    assert Nonce.objects.count() == 0
