import datetime
from unittest import mock

import pytest
from django.contrib.auth.hashers import make_password
from freezegun import freeze_time

from ami.fi.models import FISession


@freeze_time("2026-04-07 17:21:00")
@pytest.mark.django_db
def test_token(
    settings,
    django_app,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    user_data = {"sub": "fake-sub"}
    nonce = "fake-nonce"
    code = "fake-code"
    fi_session = FISession.objects.create(user_data=user_data, nonce=nonce, code=code)
    token_data = {
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": settings.FC_AMI_REDIRECT_URL,
        "client_id": settings.FI_CLIENT_ID,
        "client_secret": settings.FI_CLIENT_SECRET,
    }

    encode_mock = mock.Mock(return_value="fake-encoded-id-token")
    monkeypatch.setattr("jwt.encode", encode_mock)

    monkeypatch.setattr("ami.fi.api_views.token_urlsafe", lambda a: "fake-access-token")
    expected_access_token = make_password("fake-access-token", settings.FI_HASH_SALT)

    response = django_app.post("/api/v1/fi/token/", token_data)
    assert response.json == {
        "access_token": "fake-access-token",
        "expires_in": 60,
        "id_token": "fake-encoded-id-token",
        "token_type": "Bearer",
    }
    encode_mock.assert_called_once_with(
        {
            "aud": "33fe498cc172fe691778912a2967baa650b24f1ae0ebbe47ae552f37b2d25ead",
            "exp": 1775582760,
            "iat": 1775582460,
            "iss": "https://localhost:8000/api/v1/fi/",
            "sub": "fake-sub",
            "nonce": "fake-nonce",
            "acr": "eidas1",
        },
        settings.FI_CLIENT_SECRET,
        algorithm="HS256",
    )
    fi_session.refresh_from_db()
    assert fi_session.access_token == expected_access_token


def test_token_invalid_data_code(
    settings,
    django_app,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    code = ""
    token_data = {
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": settings.FC_AMI_REDIRECT_URL,
        "client_id": settings.FI_CLIENT_ID,
        "client_secret": settings.FI_CLIENT_SECRET,
    }

    response = django_app.post("/api/v1/fi/token/", token_data, status=400)
    assert response.json == {"code": ["Ce champ ne peut être vide."]}


def test_token_invalid_grant_type(
    settings,
    django_app,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    code = "fake-code"
    token_data = {
        "code": code,
        "grant_type": "invalid-grant-type",
        "redirect_uri": settings.FC_AMI_REDIRECT_URL,
        "client_id": settings.FI_CLIENT_ID,
        "client_secret": settings.FI_CLIENT_SECRET,
    }

    response = django_app.post("/api/v1/fi/token/", token_data, status=400)
    assert response.json == {
        "grant_type": ["'grant_type' doit être 'authorization_code', trouvé 'invalid-grant-type'"]
    }


def test_token_invalid_redirect_uri(
    settings,
    django_app,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    code = "fake-code"
    token_data = {
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": "invalid-redirect-uri",
        "client_id": settings.FI_CLIENT_ID,
        "client_secret": settings.FI_CLIENT_SECRET,
    }

    response = django_app.post("/api/v1/fi/token/", token_data, status=400)
    assert response.json == {
        "redirect_uri": [
            f"'redirect_uri' doit être '{settings.FC_AMI_REDIRECT_URL}', trouvé 'invalid-redirect-uri'"
        ]
    }


def test_token_invalid_client_id(
    settings,
    django_app,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    code = "fake-code"
    token_data = {
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": settings.FC_AMI_REDIRECT_URL,
        "client_id": "invalid-client-id",
        "client_secret": settings.FI_CLIENT_SECRET,
    }

    response = django_app.post("/api/v1/fi/token/", token_data, status=400)
    assert response.json == {"client_id": ["'client_id' invalide"]}


def test_token_invalid_client_secret(
    settings,
    django_app,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    code = "fake-code"
    token_data = {
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": settings.FC_AMI_REDIRECT_URL,
        "client_id": settings.FI_CLIENT_ID,
        "client_secret": "invalid-client-secret",
    }

    response = django_app.post("/api/v1/fi/token/", token_data, status=400)
    assert response.json == {"client_secret": ["'client_secret' invalide"]}


@pytest.mark.django_db
def test_token_fi_session_expired(
    settings,
    django_app,
) -> None:
    user_data = {"sub": "fake-sub"}
    nonce = "fake-nonce"
    code = "fake-code"
    fi_session = FISession.objects.create(user_data=user_data, nonce=nonce, code=code)
    fi_session.created_at -= datetime.timedelta(seconds=settings.FI_SESSION_AGE)
    fi_session.save()
    token_data = {
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": settings.FC_AMI_REDIRECT_URL,
        "client_id": settings.FI_CLIENT_ID,
        "client_secret": settings.FI_CLIENT_SECRET,
    }

    response = django_app.post("/api/v1/fi/token/", token_data, status=403)
    assert response.json == {"detail": "Session de connexion à AMI-FI expirée"}


@pytest.mark.django_db
def test_token_fi_session_not_found(
    settings,
    django_app,
) -> None:
    user_data = {"sub": "fake-sub"}
    nonce = "fake-nonce"
    code = "fake-code"
    FISession.objects.create(user_data=user_data, nonce=nonce, code="other-code")
    token_data = {
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": settings.FC_AMI_REDIRECT_URL,
        "client_id": settings.FI_CLIENT_ID,
        "client_secret": settings.FI_CLIENT_SECRET,
    }

    response = django_app.post("/api/v1/fi/token/", token_data, status=403)
    assert response.json == {"detail": "Session de connexion à AMI-FI non trouvée"}
