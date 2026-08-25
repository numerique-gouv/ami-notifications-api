import base64
import json
import uuid
from typing import Any
from unittest import mock

import pytest
from django.contrib.auth.hashers import make_password
from django.core import signing
from webauthn.helpers.exceptions import InvalidAuthenticationResponse

from ami.fi.models import FISession, UserPasskey
from ami.tests.utils import login, url_contains_param
from ami.user.models import User


@pytest.mark.django_db
def test_passkey_authentication(
    settings,
    app,
    monkeypatch: pytest.MonkeyPatch,
    userinfo: dict[str, Any],
    decoded_user_data: dict[str, Any],
    user: User,
) -> None:
    def fake_jwt_decode(*args: Any, **params: Any):
        return userinfo

    settings.PUBLIC_FC_PROXY_BASE_URL = ""

    monkeypatch.setattr("jwt.decode", fake_jwt_decode)

    monkeypatch.setattr("ami.fi.api_views.token_urlsafe", lambda a: "fake-code")
    expected_code = make_password("fake-code", settings.FI_HASH_SALT)

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
    assert app.session["fi_session_id"]
    assert response.location == "/?redirect_to_hash=#/passkey-authentication"

    response = app.post_json(
        "/api/v1/fi/passkey/verify-authentication", {"id": "fake-credential-id"}
    )

    fi_session = FISession.objects.get()
    assert fi_session.user_data == decoded_user_data
    assert fi_session.state == "fake-state"
    assert fi_session.nonce == "fake-nonce"
    assert fi_session.code == expected_code
    assert fi_session.access_token == ""
    redirected_url = response.json["redirect_uri"]
    assert redirected_url.startswith(settings.FI_REDIRECT_URI)
    assert url_contains_param(
        "code",
        "fake-code",
        redirected_url,
    )
    assert url_contains_param(
        "state",
        "fake-state",
        redirected_url,
    )

    assert app.session.get("fi_session_id") is None
    assert app.session.get("passkey_authentication_challenge") is None


@pytest.mark.django_db
def test_passkey_authentication_with_proxy(
    settings,
    app,
    monkeypatch: pytest.MonkeyPatch,
    userinfo: dict[str, Any],
    decoded_user_data: dict[str, Any],
    user: User,
) -> None:
    def fake_jwt_decode(*args: Any, **params: Any):
        return userinfo

    settings.PUBLIC_FC_PROXY_BASE_URL = "https://ami-fc-proxy"

    monkeypatch.setattr("jwt.decode", fake_jwt_decode)

    monkeypatch.setattr("ami.fi.api_views.token_urlsafe", lambda a: "fake-code")
    expected_code = make_password("fake-code", settings.FI_HASH_SALT)

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

    app.get("/api/v1/fi/authorize/", params=authorize_data)
    assert app.session["fi_session_id"]

    response = app.post_json(
        "/api/v1/fi/passkey/verify-authentication", {"id": "fake-credential-id"}
    )

    fi_session = FISession.objects.get()
    assert fi_session.user_data == decoded_user_data
    assert fi_session.state == "fake-state"
    assert fi_session.nonce == "fake-nonce"
    assert fi_session.code == expected_code
    assert fi_session.access_token == ""
    redirected_url = response.json["redirect_uri"]
    assert redirected_url.startswith(
        f"{settings.PUBLIC_FC_PROXY_BASE_URL}/ami-fi-authorize-callback/"
    )
    redirect_uri = f"{settings.FI_REDIRECT_URI}?code=fake-code&state=fake-state"
    assert url_contains_param(
        "redirect_uri",
        redirect_uri,
        redirected_url,
    )

    assert app.session.get("fi_session_id") is None
    assert app.session.get("passkey_authentication_challenge") is None


@pytest.mark.django_db
def test_passkey_authentication_missing_challenge(
    settings,
    app,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    response = app.post_json("/api/v1/fi/passkey/verify-authentication", status=400)
    assert response.json == {"error": "missing-challenge"}

    assert app.session.get("fi_session_id") is None
    assert app.session.get("passkey_authentication_challenge") is None


@pytest.mark.django_db
def test_passkey_authentication_missing_credential_id(
    settings,
    app,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    app.get(
        "/api/v1/fi/passkey/generate-authentication-options",
    )
    assert app.session.get("passkey_authentication_challenge") is not None

    response = app.post_json("/api/v1/fi/passkey/verify-authentication", {}, status=400)
    assert response.json == {"error": "missing-credential-id"}

    assert app.session.get("fi_session_id") is None
    assert app.session.get("passkey_authentication_challenge") is None


@pytest.mark.django_db
def test_passkey_authentication_user_passkey_not_found(
    settings,
    app,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    app.get(
        "/api/v1/fi/passkey/generate-authentication-options",
    )
    assert app.session.get("passkey_authentication_challenge") is not None

    response = app.post_json(
        "/api/v1/fi/passkey/verify-authentication", {"id": "missing-credential-id"}, status=400
    )
    assert response.json == {"error": "unknown-credential-id"}

    assert app.session.get("fi_session_id") is None
    assert app.session.get("passkey_authentication_challenge") is None


@pytest.mark.django_db
def test_passkey_authentication_verify_failed(
    settings,
    app,
    monkeypatch: pytest.MonkeyPatch,
    user: User,
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
        "/api/v1/fi/passkey/verify-authentication", {"id": "fake-credential-id"}, status=400
    )
    assert response.json == {
        "error": "invalid-authentication-response",
        "error-details": "mocked verify_authentication_response error",
    }

    assert app.session.get("fi_session_id") is None
    assert app.session.get("passkey_authentication_challenge") is None


@pytest.mark.django_db
def test_passkey_authentication_missing_fi_session_id(
    settings,
    app,
    monkeypatch: pytest.MonkeyPatch,
    user: User,
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
    assert app.session["fi_session_id"]
    # delete fi_session_id
    session = app.session
    del session["fi_session_id"]
    session.save()

    response = app.post_json(
        "/api/v1/fi/passkey/verify-authentication", {"id": "fake-credential-id"}, status=400
    )
    assert response.json == {"error": "missing-fi-session"}

    assert app.session.get("fi_session_id") is None
    assert app.session.get("passkey_authentication_challenge") is None


@pytest.mark.django_db
def test_passkey_authentication_unknown_fi_session_id(
    settings,
    app,
    monkeypatch: pytest.MonkeyPatch,
    user: User,
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
    assert app.session["fi_session_id"]
    # change fi_session_id
    session = app.session
    session["fi_session_id"] = str(uuid.uuid4())
    session.save()

    response = app.post_json(
        "/api/v1/fi/passkey/verify-authentication", {"id": "fake-credential-id"}, status=400
    )
    assert response.json == {"error": "unknown-fi-session"}

    assert app.session.get("fi_session_id") is None
    assert app.session.get("passkey_authentication_challenge") is None


@pytest.mark.django_db
def test_passkey_authentication_invalid_fi_session_id(
    settings,
    app,
    monkeypatch: pytest.MonkeyPatch,
    user: User,
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
    assert app.session["fi_session_id"]
    # change fi_session_id
    session = app.session
    session["fi_session_id"] = "not-a-uuid"
    session.save()

    response = app.post_json(
        "/api/v1/fi/passkey/verify-authentication", {"id": "fake-credential-id"}, status=400
    )
    assert response.json == {"error": "invalid-fi-session"}

    assert app.session.get("fi_session_id") is None
    assert app.session.get("passkey_authentication_challenge") is None


@pytest.mark.django_db
def test_passkey_authentication_missing_cookie(
    settings,
    app,
    monkeypatch: pytest.MonkeyPatch,
    user: User,
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
    assert app.session["fi_session_id"]

    response = app.post_json(
        "/api/v1/fi/passkey/verify-authentication", {"id": "fake-credential-id"}, status=403
    )
    assert response.json == {"error": "missing-cookie"}

    assert app.session.get("fi_session_id") is None
    assert app.session.get("passkey_authentication_challenge") is None


@pytest.mark.django_db
def test_passkey_authentication_fc_hash_mismatch(
    settings,
    app,
    monkeypatch: pytest.MonkeyPatch,
    userinfo: dict[str, Any],
    decoded_user_data: dict[str, Any],
    two_users: list[User],
) -> None:
    def fake_jwt_decode(*args: Any, **params: Any):
        return userinfo

    user, second_user = two_users

    settings.PUBLIC_FC_PROXY_BASE_URL = ""

    monkeypatch.setattr("jwt.decode", fake_jwt_decode)

    monkeypatch.setattr("ami.fi.api_views.token_urlsafe", lambda a: "fake-code")

    app.set_cookie(settings.USERINFO_COOKIE_NAME, signing.dumps(decoded_user_data))

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
    assert app.session["fi_session_id"]

    response = app.post_json(
        "/api/v1/fi/passkey/verify-authentication", {"id": "fake-credential-id"}, status=403
    )
    assert response.json == {"error": "difference-in-fc-hash"}

    assert app.session.get("fi_session_id") is None
    assert app.session.get("passkey_authentication_challenge") is None


@pytest.mark.django_db
def test_passkey_authentication_ami_user_mismatch(
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

    settings.PUBLIC_FC_PROXY_BASE_URL = ""

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
    assert app.session["fi_session_id"]

    response = app.post_json(
        "/api/v1/fi/passkey/verify-authentication",
        {"id": "second-fake-credential-id"},
        status=403,
    )
    assert response.json == {"error": "user-is-not-ami-user"}

    assert app.session.get("fi_session_id") is None
    assert app.session.get("passkey_authentication_challenge") is None


@pytest.mark.django_db
def test_authorize_relogin(
    settings,
    app,
    user: User,
) -> None:
    login(app, user)

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
    assert response.location == "/#/relogin"
