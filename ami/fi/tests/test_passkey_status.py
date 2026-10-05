import pytest

from ami.fi.models import UserPasskey
from ami.tests.utils import assert_query_fails_without_auth, login
from ami.user.models import User


@pytest.mark.django_db
def test_passkey_status_user_has_no_passkey(
    app,
    user: User,
) -> None:
    login(app, user)

    response = app.get("/api/v1/fi/passkey/status")

    assert response.json == {"has_passkey": False}


@pytest.mark.django_db
def test_passkey_status_user_has_one_passkey(
    app,
    user: User,
) -> None:
    login(app, user)

    UserPasskey.objects.create(
        user=user,
        credential_id="fake-credential-id",
    )
    response = app.get("/api/v1/fi/passkey/status")

    assert response.json == {"has_passkey": True}


@pytest.mark.django_db
def test_passkey_status_user_has_many_passkeys(
    app,
    user: User,
) -> None:
    login(app, user)

    UserPasskey.objects.create(
        user=user,
        credential_id="fake-credential-id",
    )
    UserPasskey.objects.create(
        user=user,
        credential_id="fake-credential-id2",
    )
    response = app.get("/api/v1/fi/passkey/status")

    assert response.json == {"has_passkey": True}


@pytest.mark.django_db
def test_passkey_status_without_auth(
    app,
) -> None:
    assert_query_fails_without_auth(app, "/api/v1/fi/passkey/status")
