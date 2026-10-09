import base64
import json
from typing import Any
from unittest import mock

import pytest
from django.core import signing
from webauthn.helpers.exceptions import InvalidAuthenticationResponse

from ami.fi.models import UserPasskey
from ami.tests.utils import login
from ami.user.models import User


@pytest.fixture
def cookie(settings, app, monkeypatch, user, decoded_user_data):
    app.set_cookie(settings.USERINFO_COOKIE_NAME, signing.dumps(decoded_user_data))


@pytest.mark.django_db
def test_passkey_authentication_check(
    settings,
    app,
    monkeypatch: pytest.MonkeyPatch,
    userinfo: dict[str, Any],
    decoded_user_data: dict[str, Any],
    user: User,
) -> None:
    def fake_jwt_decode(*args: Any, **params: Any):
        return userinfo

    monkeypatch.setattr("jwt.decode", fake_jwt_decode)

    monkeypatch.setattr("ami.fi.api_views.token_urlsafe", lambda a: "fake-code")

    app.set_cookie(settings.USERINFO_COOKIE_NAME, signing.dumps(decoded_user_data))

    UserPasskey.objects.create(
        user=user,
        credential_id="fake-credential-id",
        credential_public_key=base64.encodebytes(b"fake-credential-public-key").decode(),
    )

    app.get(
        "/api/v1/fi/passkey/generate-authentication-options",
    )
    assert app.session.get("passkey_authentication_challenge") is not None

    monkeypatch.setattr(
        "ami.fi.api_views.verify_authentication_response",
        lambda *a, **b: mock.MagicMock(user_verified=True),
    )
    monkeypatch.setattr("ami.fi.api_views.build_fc_hash", lambda **b: user.fc_hash)

    authorize_data = {
        "state": "fake-state",
        "nonce": "fake-nonce",
        "response_type": "code",
        "client_id": settings.FI_CLIENT_ID,
        "redirect_uri": settings.FI_REDIRECT_URI,
        "scope": "fake-scope",
        "acr_values": "eidas1",
        "claims": json.dumps(
            {
                "id_token": "fake-id-token",
            }
        ),
        "prompt": "fake-prompt",
    }

    response = app.get("/api/v1/fi/authorize/", params=authorize_data)
    assert response.location == "/?redirect_to_hash=#/passkey-authentication"

    response = app.post_json(
        "/api/v1/fi/passkey/verify-authentication-check", {"id": "fake-credential-id"}
    )
    assert response.json == {"verified": True, "redirect_uri": ""}


@pytest.mark.django_db
def test_passkey_authentication_check_missing_cookie(
    settings,
    app,
    monkeypatch: pytest.MonkeyPatch,
    user: User,
) -> None:
    app.get(
        "/api/v1/fi/passkey/generate-authentication-options",
    )
    assert app.session.get("passkey_authentication_challenge") is not None

    monkeypatch.setattr(
        "ami.fi.api_views.verify_authentication_response",
        lambda *a, **b: mock.MagicMock(user_verified=True),
    )

    authorize_data = {
        "state": "fake-state",
        "nonce": "fake-nonce",
        "response_type": "code",
        "client_id": settings.FI_CLIENT_ID,
        "redirect_uri": settings.FI_REDIRECT_URI,
        "scope": "fake-scope",
        "acr_values": "eidas1",
        "claims": json.dumps(
            {
                "id_token": "fake-id-token",
            }
        ),
        "prompt": "fake-prompt",
    }

    app.get("/api/v1/fi/authorize/", params=authorize_data)

    response = app.post_json(
        "/api/v1/fi/passkey/verify-authentication-check", {"id": "fake-credential-id"}, status=403
    )
    assert response.json == {"error": "missing-cookie"}

    assert app.session.get("passkey_authentication_challenge") is None


@pytest.mark.django_db
def test_passkey_authentication_check_missing_challenge(
    app,
    cookie,
) -> None:
    response = app.post_json("/api/v1/fi/passkey/verify-authentication-check", status=400)
    assert response.json == {"error": "missing-challenge", "retry": True}

    assert app.session.get("passkey_authentication_challenge") is None


@pytest.mark.django_db
def test_passkey_authentication_check_missing_credential_id(
    app,
    cookie,
) -> None:
    app.get(
        "/api/v1/fi/passkey/generate-authentication-options",
    )
    assert app.session.get("passkey_authentication_challenge") is not None

    response = app.post_json("/api/v1/fi/passkey/verify-authentication-check", {}, status=400)
    assert response.json == {"error": "missing-credential-id", "retry": True}

    assert app.session.get("passkey_authentication_challenge") is None


@pytest.mark.django_db
def test_passkey_authentication_check_user_passkey_not_found(
    app,
    cookie,
) -> None:
    app.get(
        "/api/v1/fi/passkey/generate-authentication-options",
    )
    assert app.session.get("passkey_authentication_challenge") is not None

    response = app.post_json(
        "/api/v1/fi/passkey/verify-authentication-check",
        {"id": "missing-credential-id"},
        status=400,
    )
    assert response.json == {"error": "unknown-credential-id", "retry": True}

    assert app.session.get("passkey_authentication_challenge") is None


@pytest.mark.django_db
def test_passkey_authentication_check_verify_failed(
    app,
    monkeypatch: pytest.MonkeyPatch,
    user: User,
    cookie,
) -> None:
    UserPasskey.objects.create(
        user=user,
        credential_id="fake-credential-id",
        credential_public_key=base64.encodebytes(b"fake-credential-public-key").decode(),
    )

    app.get(
        "/api/v1/fi/passkey/generate-authentication-options",
    )
    assert app.session.get("passkey_authentication_challenge") is not None

    def mocked_verify_authentication_response(**kwargs):
        raise InvalidAuthenticationResponse("mocked verify_authentication_response error")

    monkeypatch.setattr(
        "ami.fi.api_views.verify_authentication_response", mocked_verify_authentication_response
    )

    response = app.post_json(
        "/api/v1/fi/passkey/verify-authentication-check", {"id": "fake-credential-id"}, status=400
    )
    assert response.json == {
        "error": "invalid-authentication-response",
        "error-details": "mocked verify_authentication_response error",
        "retry": True,
    }

    assert app.session.get("passkey_authentication_challenge") is None


@pytest.mark.django_db
def test_passkey_authentication_check_fc_hash_mismatch(
    settings,
    app,
    monkeypatch: pytest.MonkeyPatch,
    userinfo: dict[str, Any],
    two_users: list[User],
    cookie,
) -> None:
    def fake_jwt_decode(*args: Any, **params: Any):
        return userinfo

    user, second_user = two_users

    monkeypatch.setattr("jwt.decode", fake_jwt_decode)

    monkeypatch.setattr("ami.fi.api_views.token_urlsafe", lambda a: "fake-code")

    UserPasskey.objects.create(
        user=second_user,
        credential_id="fake-credential-id",
        credential_public_key=base64.encodebytes(b"fake-credential-public-key").decode(),
    )

    app.get(
        "/api/v1/fi/passkey/generate-authentication-options",
    )
    assert app.session.get("passkey_authentication_challenge") is not None

    monkeypatch.setattr(
        "ami.fi.api_views.verify_authentication_response",
        lambda *a, **b: mock.MagicMock(user_verified=True),
    )
    monkeypatch.setattr("ami.fi.api_views.build_fc_hash", lambda **b: user.fc_hash)

    authorize_data = {
        "state": "fake-state",
        "nonce": "fake-nonce",
        "response_type": "code",
        "client_id": settings.FI_CLIENT_ID,
        "redirect_uri": settings.FI_REDIRECT_URI,
        "scope": "fake-scope",
        "acr_values": "eidas1",
        "claims": json.dumps(
            {
                "id_token": "fake-id-token",
            }
        ),
        "prompt": "fake-prompt",
    }

    app.get("/api/v1/fi/authorize/", params=authorize_data)

    response = app.post_json(
        "/api/v1/fi/passkey/verify-authentication-check", {"id": "fake-credential-id"}, status=403
    )
    assert response.json == {"error": "difference-in-fc-hash", "retry": True}

    assert app.session.get("passkey_authentication_challenge") is None


@pytest.mark.django_db
def test_passkey_authentication_check_ami_user_mismatch(
    settings,
    app,
    monkeypatch: pytest.MonkeyPatch,
    userinfo: dict[str, Any],
    decoded_user_data: dict[str, Any],
    two_users: list[User],
) -> None:
    user, second_user = two_users
    userinfo["sub"] = str(user.id)
    login(app, user)

    def fake_jwt_decode(*args: Any, **params: Any):
        return userinfo

    monkeypatch.setattr("jwt.decode", fake_jwt_decode)

    monkeypatch.setattr("ami.fi.api_views.token_urlsafe", lambda a: "fake-code")

    app.set_cookie(settings.USERINFO_COOKIE_NAME, signing.dumps(decoded_user_data))

    UserPasskey.objects.create(
        user=user,
        credential_id="fake-credential-id",
        credential_public_key=base64.encodebytes(b"fake-credential-public-key").decode(),
    )
    UserPasskey.objects.create(
        user=second_user,
        credential_id="second-fake-credential-id",
        credential_public_key=base64.encodebytes(b"second-fake-credential-public-key").decode(),
    )

    app.get(
        "/api/v1/fi/passkey/generate-authentication-options",
    )
    assert app.session.get("passkey_authentication_challenge") is not None

    monkeypatch.setattr(
        "ami.fi.api_views.verify_authentication_response",
        lambda *a, **b: mock.MagicMock(user_verified=True),
    )
    monkeypatch.setattr("ami.fi.api_views.build_fc_hash", lambda **b: second_user.fc_hash)

    authorize_data = {
        "state": "fake-state",
        "nonce": "fake-nonce",
        "response_type": "code",
        "client_id": settings.FI_CLIENT_ID,
        "redirect_uri": settings.FI_REDIRECT_URI,
        "scope": "fake-scope",
        "acr_values": "eidas1",
        "claims": json.dumps(
            {
                "id_token": "fake-id-token",
            }
        ),
        "prompt": "fake-prompt",
    }

    app.get("/api/v1/fi/authorize/", params=authorize_data)

    response = app.post_json(
        "/api/v1/fi/passkey/verify-authentication-check",
        {"id": "second-fake-credential-id"},
        status=403,
    )
    assert response.json == {"error": "user-is-not-ami-user", "retry": True}

    assert app.session.get("passkey_authentication_challenge") is None
