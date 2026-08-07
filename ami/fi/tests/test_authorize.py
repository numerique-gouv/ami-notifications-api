import json
from typing import Any

import pytest

from ami.fi.models import FISession


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

    redirected_url = response.headers["location"]
    assert redirected_url == "/#/passkey-authentication"


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


def test_authorize_flag_disabled(
    settings,
    app,
) -> None:
    settings.FI_SILENT_LOGIN_ENABLED = False
    app.get("/api/v1/fi/authorize/", status=404)
