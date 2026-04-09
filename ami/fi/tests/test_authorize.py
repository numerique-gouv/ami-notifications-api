import json
from typing import Any

import pytest
from django.contrib.auth.hashers import make_password

from ami.fi.models import FISession
from ami.tests.utils import url_contains_param


@pytest.mark.django_db
def test_authorize(
    settings,
    app,
    monkeypatch: pytest.MonkeyPatch,
    userinfo: dict[str, Any],
) -> None:
    def fake_jwt_decode(*args: Any, **params: Any):
        return userinfo

    monkeypatch.setattr("jwt.decode", fake_jwt_decode)

    monkeypatch.setattr("ami.fi.api_views.token_urlsafe", lambda a: "fake-code")
    expected_code = make_password("fake-code", settings.FI_HASH_SALT)

    app.set_cookie(settings.USERINFO_COOKIE_JWT_NAME, "fake userinfo jwt token")

    authorize_data = {
        "state": "fake-state",
        "nonce": "fake-nonce",
        "response_type": "code",
        "client_id": settings.FI_CLIENT_ID,
        "redirect_uri": settings.FC_AMI_REDIRECT_URL,
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
    assert response.status_code == 302
    fi_session = FISession.objects.get()
    assert fi_session.user_data == userinfo
    assert fi_session.state == "fake-state"
    assert fi_session.nonce == "fake-nonce"
    assert fi_session.code == expected_code
    assert fi_session.access_token == ""
    redirected_url = response.headers["location"]
    assert redirected_url.startswith(settings.FC_AMI_REDIRECT_URL)
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


def test_authorize_invalid_data_state(
    settings,
    app,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    authorize_data = {
        "state": "",
        "nonce": "fake-nonce",
        "response_type": "code",
        "client_id": settings.FI_CLIENT_ID,
        "redirect_uri": settings.FC_AMI_REDIRECT_URL,
        "scope": "fake-scope",
        "acr_values": "eidas1",
        "claims": json.dumps(
            {
                "id_token": "fake-id-token",
            }
        ),
        "prompt": "fake-prompt",
    }

    response = app.get("/api/v1/fi/authorize/", params=authorize_data, status=400)
    assert response.json == {"state": ["Ce champ ne peut être vide."]}


def test_authorize_invalid_data_nonce(
    settings,
    app,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    authorize_data = {
        "state": "fake-state",
        "nonce": "",
        "response_type": "code",
        "client_id": settings.FI_CLIENT_ID,
        "redirect_uri": settings.FC_AMI_REDIRECT_URL,
        "scope": "fake-scope",
        "acr_values": "eidas1",
        "claims": json.dumps(
            {
                "id_token": "fake-id-token",
            }
        ),
        "prompt": "fake-prompt",
    }

    response = app.get("/api/v1/fi/authorize/", params=authorize_data, status=400)
    assert response.json == {"nonce": ["Ce champ ne peut être vide."]}


def test_authorize_invalid_data_response_type(
    settings,
    app,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    authorize_data = {
        "state": "fake-state",
        "nonce": "fake-nonce",
        "response_type": "invalid-response-type",
        "client_id": settings.FI_CLIENT_ID,
        "redirect_uri": settings.FC_AMI_REDIRECT_URL,
        "scope": "fake-scope",
        "acr_values": "eidas1",
        "claims": json.dumps(
            {
                "id_token": "fake-id-token",
            }
        ),
        "prompt": "fake-prompt",
    }

    response = app.get("/api/v1/fi/authorize/", params=authorize_data, status=400)
    assert response.json == {
        "response_type": ["'response_type' doit être 'code', trouvé 'invalid-response-type'"]
    }


def test_authorize_invalid_data_client_id(
    settings,
    app,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    authorize_data = {
        "state": "fake-state",
        "nonce": "fake-nonce",
        "response_type": "code",
        "client_id": "invalid-client-id",
        "redirect_uri": settings.FC_AMI_REDIRECT_URL,
        "scope": "fake-scope",
        "acr_values": "eidas1",
        "claims": json.dumps(
            {
                "id_token": "fake-id-token",
            }
        ),
        "prompt": "fake-prompt",
    }

    response = app.get("/api/v1/fi/authorize/", params=authorize_data, status=400)
    assert response.json == {"client_id": ["'client_id' invalide"]}


def test_authorize_invalid_data_redirect_uri(
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

    response = app.get("/api/v1/fi/authorize/", params=authorize_data, status=400)
    assert response.json == {
        "redirect_uri": [
            "'redirect_uri' doit être 'https://localhost:8000/login-callback', trouvé 'invalid-redirect-uri'"
        ]
    }


def test_authorize_invalid_data_scope(
    settings,
    app,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    authorize_data = {
        "state": "fake-state",
        "nonce": "fake-nonce",
        "response_type": "code",
        "client_id": settings.FI_CLIENT_ID,
        "redirect_uri": settings.FC_AMI_REDIRECT_URL,
        "scope": "",
        "acr_values": "eidas1",
        "claims": json.dumps(
            {
                "id_token": "fake-id-token",
            }
        ),
        "prompt": "fake-prompt",
    }

    response = app.get("/api/v1/fi/authorize/", params=authorize_data, status=400)
    assert response.json == {"scope": ["Ce champ ne peut être vide."]}


def test_authorize_invalid_acr_values(
    settings,
    app,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    authorize_data = {
        "state": "fake-state",
        "nonce": "fake-nonce",
        "response_type": "code",
        "client_id": settings.FI_CLIENT_ID,
        "redirect_uri": settings.FC_AMI_REDIRECT_URL,
        "scope": "fake-scope",
        "acr_values": "invalid-acr-values",
        "claims": json.dumps(
            {
                "id_token": "fake-id-token",
            }
        ),
        "prompt": "fake-prompt",
    }

    response = app.get("/api/v1/fi/authorize/", params=authorize_data, status=400)
    assert response.json == {
        "acr_values": ["'acr_values' doit être 'eidas1', trouvé 'invalid-acr-values'"]
    }


def test_authorize_invalid_data_claims(
    settings,
    app,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    authorize_data = {
        "state": "fake-state",
        "nonce": "fake-nonce",
        "response_type": "code",
        "client_id": settings.FI_CLIENT_ID,
        "redirect_uri": settings.FC_AMI_REDIRECT_URL,
        "scope": "fake-scope",
        "acr_values": "eidas1",
        "claims": "",
        "prompt": "fake-prompt",
    }

    response = app.get("/api/v1/fi/authorize/", params=authorize_data, status=400)
    assert response.json == {"claims": ["La valeur doit être un JSON valide."]}


def test_authorize_invalid_data_prompt(
    settings,
    app,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    authorize_data = {
        "state": "fake-state",
        "nonce": "fake-nonce",
        "response_type": "code",
        "client_id": settings.FI_CLIENT_ID,
        "redirect_uri": settings.FC_AMI_REDIRECT_URL,
        "scope": "fake-scope",
        "acr_values": "eidas1",
        "claims": json.dumps(
            {
                "id_token": "fake-id-token",
            }
        ),
        "prompt": "",
    }

    response = app.get("/api/v1/fi/authorize/", params=authorize_data, status=400)
    assert response.json == {"prompt": ["Ce champ ne peut être vide."]}


def test_authorize_missing_cookie(
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
        "redirect_uri": settings.FC_AMI_REDIRECT_URL,
        "scope": "fake-scope",
        "acr_values": "eidas1",
        "claims": json.dumps(
            {
                "id_token": "fake-id-token",
            }
        ),
        "prompt": "fake-prompt",
    }

    response = app.get("/api/v1/fi/authorize/", params=authorize_data, status=403)
    assert response.json == {"detail": "Cookie manquant"}
