import base64
import json
import uuid
from typing import Any
from unittest import mock

import pytest
from django.contrib.auth.hashers import make_password

from ami.fi.models import FISession, UserPasskey
from ami.tests.utils import url_contains_param
from ami.user.models import User


@pytest.mark.django_db
def test_verify_authentication(
    settings,
    app,
    monkeypatch: pytest.MonkeyPatch,
    userinfo: dict[str, Any],
    user: User,
) -> None:
    def fake_jwt_decode(*args: Any, **params: Any):
        return userinfo

    settings.PUBLIC_FC_PROXY_BASE_URL = ""

    app.set_cookie("sessionid", "initial")
    session = app.session
    session["passkey_authentication_challenge"] = base64.encodebytes(b"fake-challenge").decode()
    session.save()
    app.set_cookie("sessionid", session.session_key)

    monkeypatch.setattr("jwt.decode", fake_jwt_decode)

    monkeypatch.setattr("ami.fi.api_views.token_urlsafe", lambda a: "fake-code")
    expected_code = make_password("fake-code", settings.FI_HASH_SALT)

    encoded_user_data = "fake userinfo jwt token"
    app.set_cookie(settings.USERINFO_COOKIE_JWT_NAME, encoded_user_data)

    UserPasskey.objects.create(
        user=user,
        credential_id="fake-credential-id",
        credential_public_key=base64.encodebytes(b"fake-credential-public-key").decode(),
    )

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
    assert fi_session.user_data == userinfo
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


@pytest.mark.django_db
def test_verify_authentication_with_proxy(
    settings,
    app,
    monkeypatch: pytest.MonkeyPatch,
    userinfo: dict[str, Any],
    user: User,
) -> None:
    def fake_jwt_decode(*args: Any, **params: Any):
        return userinfo

    settings.PUBLIC_FC_PROXY_BASE_URL = "https://ami-fc-proxy"

    app.set_cookie("sessionid", "initial")
    session = app.session
    session["passkey_authentication_challenge"] = base64.encodebytes(b"fake-challenge").decode()
    session.save()
    app.set_cookie("sessionid", session.session_key)

    monkeypatch.setattr("jwt.decode", fake_jwt_decode)

    monkeypatch.setattr("ami.fi.api_views.token_urlsafe", lambda a: "fake-code")
    expected_code = make_password("fake-code", settings.FI_HASH_SALT)

    encoded_user_data = "fake userinfo jwt token"
    app.set_cookie(settings.USERINFO_COOKIE_JWT_NAME, encoded_user_data)

    UserPasskey.objects.create(
        user=user,
        credential_id="fake-credential-id",
        credential_public_key=base64.encodebytes(b"fake-credential-public-key").decode(),
    )

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
    assert fi_session.user_data == userinfo
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


@pytest.mark.django_db
def test_verify_authentication_missing_challenge(
    settings,
    app,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    pass


@pytest.mark.django_db
def test_verify_authentication_missing_credential_id(
    settings,
    app,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    pass


@pytest.mark.django_db
def test_verify_authentication_user_passkey_not_found(
    settings,
    app,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    pass


@pytest.mark.django_db
def test_verify_authentication_verify_failed(
    settings,
    app,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    pass


@pytest.mark.django_db
def test_verify_authentication_missing_fi_session_id(
    settings,
    app,
    monkeypatch: pytest.MonkeyPatch,
    user: User,
) -> None:
    app.set_cookie("sessionid", "initial")
    session = app.session
    session["passkey_authentication_challenge"] = base64.encodebytes(b"fake-challenge").decode()
    session.save()
    app.set_cookie("sessionid", session.session_key)

    UserPasskey.objects.create(
        user=user,
        credential_id="fake-credential-id",
        credential_public_key=base64.encodebytes(b"fake-credential-public-key").decode(),
    )

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
    assert response.content == b"missing-fi-session"


@pytest.mark.django_db
def test_verify_authentication_unknown_fi_session_id(
    settings,
    app,
    monkeypatch: pytest.MonkeyPatch,
    user: User,
) -> None:
    app.set_cookie("sessionid", "initial")
    session = app.session
    session["passkey_authentication_challenge"] = base64.encodebytes(b"fake-challenge").decode()
    session.save()
    app.set_cookie("sessionid", session.session_key)

    UserPasskey.objects.create(
        user=user,
        credential_id="fake-credential-id",
        credential_public_key=base64.encodebytes(b"fake-credential-public-key").decode(),
    )

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
    assert response.content == b"unkown-fi-session"


@pytest.mark.django_db
def test_verify_authentication_invalid_fi_session_id(
    settings,
    app,
    monkeypatch: pytest.MonkeyPatch,
    user: User,
) -> None:
    app.set_cookie("sessionid", "initial")
    session = app.session
    session["passkey_authentication_challenge"] = base64.encodebytes(b"fake-challenge").decode()
    session.save()
    app.set_cookie("sessionid", session.session_key)

    UserPasskey.objects.create(
        user=user,
        credential_id="fake-credential-id",
        credential_public_key=base64.encodebytes(b"fake-credential-public-key").decode(),
    )

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
    assert response.content == b"invalid-fi-session"


@pytest.mark.django_db
def test_verify_authentication_missing_cookie(
    settings,
    app,
    monkeypatch: pytest.MonkeyPatch,
    user: User,
) -> None:
    app.set_cookie("sessionid", "initial")
    session = app.session
    session["passkey_authentication_challenge"] = base64.encodebytes(b"fake-challenge").decode()
    session.save()
    app.set_cookie("sessionid", session.session_key)

    UserPasskey.objects.create(
        user=user,
        credential_id="fake-credential-id",
        credential_public_key=base64.encodebytes(b"fake-credential-public-key").decode(),
    )

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
    assert response.content == b"missing-cookie"


@pytest.mark.django_db
def test_verify_authentication_fc_hash_mismatch(
    settings,
    app,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    pass
