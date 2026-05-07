import datetime

import pytest
from django.conf import settings
from django.contrib.auth.hashers import make_password

from ami.fi.models import FISession


@pytest.mark.django_db
def test_userinfo(
    app,
) -> None:
    auth_token = "fake-access-token"
    auth_token_hash = make_password(auth_token, settings.FI_HASH_SALT)
    user_data = {"fake-key": "fake-user-data"}
    FISession.objects.create(user_data=user_data, access_token=auth_token_hash)
    response = app.get("/api/v1/fi/userinfo/", headers={"AUTHORIZATION": f"Bearer {auth_token}"})
    assert response.json == user_data


@pytest.mark.django_db
def test_userinfo_missing_auth_header(
    app,
) -> None:
    user_data = {"fake-key": "fake-user-data"}
    FISession.objects.create(user_data=user_data, access_token="fake-access-token")
    response = app.get("/api/v1/fi/userinfo/", status=403)
    assert response.json == {"detail": "Header d'authentification manquant"}


@pytest.mark.django_db
def test_userinfo_wrong_format_auth_header(
    app,
) -> None:
    auth_token = "fake-access-token"
    user_data = {"fake-key": "fake-user-data"}
    FISession.objects.create(user_data=user_data, access_token="fake-access-token")
    response = app.get("/api/v1/fi/userinfo/", headers={"AUTHORIZATION": auth_token}, status=403)
    assert response.json == {"detail": "Header d'authentification mal formé"}


@pytest.mark.django_db
def test_userinfo_fi_session_expired(
    app,
) -> None:
    auth_token = "fake-access-token"
    auth_token_hash = make_password(auth_token, settings.FI_HASH_SALT)
    user_data = {"fake-key": "fake-user-data"}
    fi_session = FISession.objects.create(user_data=user_data, access_token=auth_token_hash)
    fi_session.created_at -= datetime.timedelta(seconds=settings.FI_SESSION_AGE)
    fi_session.save()
    response = app.get(
        "/api/v1/fi/userinfo/", headers={"AUTHORIZATION": f"Bearer {auth_token}"}, status=403
    )
    assert response.json == {"detail": "Session de connexion à AMI-FI expirée"}


@pytest.mark.django_db
def test_userinfo_fi_session_not_found(
    app,
) -> None:
    user_data = {"fake-key": "fake-user-data"}
    FISession.objects.create(user_data=user_data, access_token="fake-access-token")
    response = app.get(
        "/api/v1/fi/userinfo/", headers={"AUTHORIZATION": "Bearer azerty"}, status=403
    )
    assert response.json == {"detail": "Session de connexion à AMI-FI non trouvée"}
