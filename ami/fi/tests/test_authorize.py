import json
import uuid
from typing import Any

import pytest
from django.contrib.auth.hashers import make_password

from ami.fi.models import FISession
from ami.tests.utils import url_contains_param


@pytest.mark.django_db
def test_authorize_get(
    settings,
    app,
    monkeypatch: pytest.MonkeyPatch,
    userinfo: dict[str, Any],
) -> None:
    settings.PUBLIC_FC_PROXY_BASE_URL = ""

    app.set_cookie(settings.USERINFO_COOKIE_JWT_NAME, "fake userinfo jwt token")

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

    fi_session = FISession.objects.get()
    assert fi_session.user_data == {}
    assert fi_session.state == "fake-state"
    assert fi_session.nonce == "fake-nonce"
    assert fi_session.code == ""
    assert fi_session.access_token == ""

    assert response.form["fi_session_id"].value == str(fi_session.id)
    assert response.form["encoded_user_data"].value == "fake userinfo jwt token"


def test_authorize_get_invalid_data_state(
    settings,
    app,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    authorize_data = {
        "state": "",
        "nonce": "fake-nonce",
        "response_type": "code",
        "client_id": settings.FI_CLIENT_ID,
        "redirect_uri": settings.FI_REDIRECT_URI,
        "scope": "fake-scope",
        "acr_values": "eidas1",
        # without claims
        "prompt": "fake-prompt",
    }

    app.get("/api/v1/fi/authorize/", params=authorize_data, status=400)


def test_authorize_get_invalid_data_nonce(
    settings,
    app,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    authorize_data = {
        "state": "fake-state",
        "nonce": "",
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

    app.get("/api/v1/fi/authorize/", params=authorize_data, status=400)


def test_authorize_get_invalid_data_response_type(
    settings,
    app,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    authorize_data = {
        "state": "fake-state",
        "nonce": "fake-nonce",
        "response_type": "invalid-response-type",
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

    app.get("/api/v1/fi/authorize/", params=authorize_data, status=400)


def test_authorize_get_invalid_data_client_id(
    settings,
    app,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    authorize_data = {
        "state": "fake-state",
        "nonce": "fake-nonce",
        "response_type": "code",
        "client_id": "invalid-client-id",
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

    app.get("/api/v1/fi/authorize/", params=authorize_data, status=400)


def test_authorize_get_invalid_data_redirect_uri(
    settings,
    app,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    authorize_data = {
        "state": "fake-state",
        "nonce": "fake-nonce",
        "response_type": "code",
        "client_id": settings.FI_CLIENT_ID,
        "redirect_uri": "invalid-redirect-uri",
        "scope": "fake-scope",
        "acr_values": "eidas1",
        "claims": json.dumps(
            {
                "id_token": "fake-id-token",
            }
        ),
        "prompt": "fake-prompt",
    }

    app.get("/api/v1/fi/authorize/", params=authorize_data, status=400)


def test_authorize_get_invalid_data_scope(
    settings,
    app,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    authorize_data = {
        "state": "fake-state",
        "nonce": "fake-nonce",
        "response_type": "code",
        "client_id": settings.FI_CLIENT_ID,
        "redirect_uri": settings.FI_REDIRECT_URI,
        "scope": "",
        "acr_values": "eidas1",
        "claims": json.dumps(
            {
                "id_token": "fake-id-token",
            }
        ),
        "prompt": "fake-prompt",
    }

    app.get("/api/v1/fi/authorize/", params=authorize_data, status=400)


def test_authorize_get_invalid_acr_values(
    settings,
    app,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    authorize_data = {
        "state": "fake-state",
        "nonce": "fake-nonce",
        "response_type": "code",
        "client_id": settings.FI_CLIENT_ID,
        "redirect_uri": settings.FI_REDIRECT_URI,
        "scope": "fake-scope",
        "acr_values": "invalid-acr-values",
        "claims": json.dumps(
            {
                "id_token": "fake-id-token",
            }
        ),
        "prompt": "fake-prompt",
    }

    app.get("/api/v1/fi/authorize/", params=authorize_data, status=400)


def test_authorize_get_invalid_data_claims(
    settings,
    app,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    authorize_data = {
        "state": "fake-state",
        "nonce": "fake-nonce",
        "response_type": "code",
        "client_id": settings.FI_CLIENT_ID,
        "redirect_uri": settings.FI_REDIRECT_URI,
        "scope": "fake-scope",
        "acr_values": "eidas1",
        "claims": "wrong value",
        "prompt": "fake-prompt",
    }

    app.get("/api/v1/fi/authorize/", params=authorize_data, status=400)


def test_authorize_get_invalid_data_prompt(
    settings,
    app,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
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
        "prompt": "",
    }

    app.get("/api/v1/fi/authorize/", params=authorize_data, status=400)


def test_authorize_get_missing_cookie(
    settings,
    app,
    monkeypatch: pytest.MonkeyPatch,
    userinfo: dict[str, Any],
) -> None:
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

    app.get("/api/v1/fi/authorize/", params=authorize_data, status=403)


@pytest.mark.django_db
def test_authorize_post(
    settings,
    app,
    monkeypatch: pytest.MonkeyPatch,
    userinfo: dict[str, Any],
) -> None:
    def fake_jwt_decode(*args: Any, **params: Any):
        return userinfo

    settings.PUBLIC_FC_PROXY_BASE_URL = ""

    monkeypatch.setattr("jwt.decode", fake_jwt_decode)

    monkeypatch.setattr("ami.fi.views.token_urlsafe", lambda a: "fake-code")
    expected_code = make_password("fake-code", settings.FI_HASH_SALT)

    app.set_cookie(settings.USERINFO_COOKIE_JWT_NAME, "fake userinfo jwt token")

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

    response = response.form.submit()
    assert response.status_code == 302
    fi_session = FISession.objects.get()
    assert fi_session.user_data == userinfo
    assert fi_session.state == "fake-state"
    assert fi_session.nonce == "fake-nonce"
    assert fi_session.code == expected_code
    assert fi_session.access_token == ""
    redirected_url = response.headers["location"]
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


@pytest.mark.django_db
def test_authorize_post_with_proxy(
    settings,
    app,
    monkeypatch: pytest.MonkeyPatch,
    userinfo: dict[str, Any],
) -> None:
    def fake_jwt_decode(*args: Any, **params: Any):
        return userinfo

    settings.PUBLIC_FC_PROXY_BASE_URL = "https://ami-fc-proxy"

    monkeypatch.setattr("jwt.decode", fake_jwt_decode)

    monkeypatch.setattr("ami.fi.views.token_urlsafe", lambda a: "fake-code")
    expected_code = make_password("fake-code", settings.FI_HASH_SALT)

    app.set_cookie(settings.USERINFO_COOKIE_JWT_NAME, "fake userinfo jwt token")

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

    response = response.form.submit()
    assert response.status_code == 302
    fi_session = FISession.objects.get()
    assert fi_session.user_data == userinfo
    assert fi_session.state == "fake-state"
    assert fi_session.nonce == "fake-nonce"
    assert fi_session.code == expected_code
    assert fi_session.access_token == ""
    redirected_url = response.headers["location"]
    assert redirected_url.startswith(
        f"{settings.PUBLIC_FC_PROXY_BASE_URL}/ami-fi-authorize-callback/"
    )
    redirect_uri = f"{settings.FI_REDIRECT_URI}?code=fake-code&state=fake-state"
    assert url_contains_param(
        "redirect_uri",
        redirect_uri,
        redirected_url,
    )


@pytest.mark.django_db
def test_authorize_post_missing_fi_session_id(
    settings,
    app,
    monkeypatch: pytest.MonkeyPatch,
    userinfo: dict[str, Any],
) -> None:
    app.set_cookie(settings.USERINFO_COOKIE_JWT_NAME, "fake userinfo jwt token")

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

    response.form["fi_session_id"] = ""
    response = response.form.submit(status=400)


@pytest.mark.django_db
def test_authorize_post_unknown_fi_session_id(
    settings,
    app,
    monkeypatch: pytest.MonkeyPatch,
    userinfo: dict[str, Any],
) -> None:
    app.set_cookie(settings.USERINFO_COOKIE_JWT_NAME, "fake userinfo jwt token")

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

    response.form["fi_session_id"] = str(uuid.uuid4())
    response = response.form.submit(status=400)


@pytest.mark.django_db
def test_authorize_post_invalid_fi_session_id(
    settings,
    app,
    monkeypatch: pytest.MonkeyPatch,
    userinfo: dict[str, Any],
) -> None:
    app.set_cookie(settings.USERINFO_COOKIE_JWT_NAME, "fake userinfo jwt token")

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

    response.form["fi_session_id"] = "not-a-uuid"
    response = response.form.submit(status=400)


@pytest.mark.django_db
def test_authorize_post_missing_fi_encoded_user_data(
    settings,
    app,
    monkeypatch: pytest.MonkeyPatch,
    userinfo: dict[str, Any],
) -> None:
    app.set_cookie(settings.USERINFO_COOKIE_JWT_NAME, "fake userinfo jwt token")

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

    response.form["encoded_user_data"] = ""
    response = response.form.submit(status=400)
