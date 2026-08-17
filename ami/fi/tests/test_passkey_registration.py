import base64
from typing import Any
from unittest import mock

import pytest
from webauthn.helpers.exceptions import InvalidRegistrationResponse

from ami.fi.models import UserPasskey
from ami.tests.utils import assert_query_fails_without_auth, login
from ami.user.models import User


@pytest.mark.django_db
def test_passkey_generate_registration_options_without_auth(
    app,
) -> None:
    assert_query_fails_without_auth(
        app, "/api/v1/fi/passkey/generate-registration-options", method="post"
    )


@pytest.mark.django_db
def test_passkey_verify_registration_without_auth(
    app,
) -> None:
    assert_query_fails_without_auth(app, "/api/v1/fi/passkey/verify-registration", method="post")


@pytest.mark.django_db
def test_passkey_registration(
    settings, app, monkeypatch: pytest.MonkeyPatch, userinfo: dict[str, Any], user: User
):
    userinfo["sub"] = str(user.id)

    login(app, user)

    def fake_jwt_decode(*args: Any, **params: Any):
        return userinfo

    monkeypatch.setattr("jwt.decode", fake_jwt_decode)

    encoded_user_data = "fake userinfo jwt token"
    app.set_cookie(settings.USERINFO_COOKIE_NAME, encoded_user_data)
    response = app.post_json(
        "/api/v1/fi/passkey/generate-registration-options",
        {"displayName": "Angela Claire Louise DUBOIS"},
    )
    assert response.json["user"]["name"] == "Angela Claire Louise DUBOIS"
    assert app.session.get("passkey_registration_challenge") is not None

    monkeypatch.setattr(
        "ami.fi.api_views.verify_registration_response",
        lambda *a, **b: mock.MagicMock(
            credential_id=b"test", credential_public_key=b"public key", user_verified=True
        ),
    )

    response = app.post("/api/v1/fi/passkey/verify-registration")
    assert response.json == {"verified": True}
    user_pass_key = UserPasskey.objects.get(user=user)
    assert user_pass_key.credential_id == base64.urlsafe_b64encode(b"test").strip(b"=").decode()
    assert user_pass_key.credential_public_key == base64.urlsafe_b64encode(b"public key").decode()
    assert app.session.get("passkey_registration_challenge") is None


@pytest.mark.django_db
def test_passkey_registration_no_display_name(
    settings, app, monkeypatch: pytest.MonkeyPatch, userinfo: dict[str, Any], user: User
):
    userinfo["sub"] = str(user.id)
    login(app, user)

    def fake_jwt_decode(*args: Any, **params: Any):
        return userinfo

    monkeypatch.setattr("jwt.decode", fake_jwt_decode)

    response = app.post_json("/api/v1/fi/passkey/generate-registration-options", status=400)
    assert response.json == {"error": "missing-display-name"}


@pytest.mark.django_db
def test_passkey_registration_missing_challenge(
    settings, app, monkeypatch: pytest.MonkeyPatch, userinfo: dict[str, Any], user: User
):
    login(app, user)

    response = app.post("/api/v1/fi/passkey/verify-registration", status=400)
    assert response.json == {"error": "missing-challenge"}


@pytest.mark.django_db
def test_passkey_registration_verify_registration_response_exception(
    settings, app, monkeypatch: pytest.MonkeyPatch, userinfo: dict[str, Any], user: User
):
    userinfo["sub"] = str(user.id)

    login(app, user)

    def fake_jwt_decode(*args: Any, **params: Any):
        return userinfo

    monkeypatch.setattr("jwt.decode", fake_jwt_decode)

    encoded_user_data = "fake userinfo jwt token"
    app.set_cookie(settings.USERINFO_COOKIE_NAME, encoded_user_data)
    response = app.post_json(
        "/api/v1/fi/passkey/generate-registration-options",
        {"displayName": "Angela Claire Louise DUBOIS"},
    )
    assert response.json["user"]["name"] == "Angela Claire Louise DUBOIS"
    assert app.session.get("passkey_registration_challenge") is not None

    def mocked_verify_registration_response(**kwargs):
        raise InvalidRegistrationResponse("mocked verify_registration_response error")

    monkeypatch.setattr(
        "ami.fi.api_views.verify_registration_response", mocked_verify_registration_response
    )

    response = app.post("/api/v1/fi/passkey/verify-registration", status=400)
    assert response.json == {
        "error": "invalid-registration-response",
        "error-details": "mocked verify_registration_response error",
    }
    assert app.session.get("passkey_registration_challenge") is None
