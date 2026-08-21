import pytest

from ami.authentication.models import Nonce
from ami.tests.utils import url_contains_param


@pytest.mark.django_db
def test_relogin(
    settings,
    app,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    settings.PUBLIC_FC_PROXY_BASE_URL = "https://fake-fc-proxy"
    FAKE_NONCE = "some-random-nonce"
    monkeypatch.setattr("ami.authentication.views.generate_nonce", lambda: FAKE_NONCE)
    response = app.get("/relogin-france-connect")
    assert Nonce.objects.count() == 1
    nonce = Nonce.objects.get()
    assert nonce.nonce == FAKE_NONCE
    assert nonce.context == {"idp": "relogin"}
    assert response.status_code == 302
    redirected_url = response.headers["location"]
    assert redirected_url.startswith("https://fcp-low.sbx.dev-franceconnect.fr/api/v2/authorize")
    assert url_contains_param(
        "scope", "openid identite_pivot preferred_username email", redirected_url
    )
    assert url_contains_param("response_type", "code", redirected_url)
    assert url_contains_param("client_id", settings.FC_AMI_CLIENT_ID, redirected_url)
    assert url_contains_param("state", f"{settings.FC_AMI_REDIRECT_URL}?state=", redirected_url)
    assert url_contains_param("nonce", nonce.nonce, redirected_url)
    assert url_contains_param("acr_values", "eidas1", redirected_url)
    assert url_contains_param("prompt", "login", redirected_url)


@pytest.mark.django_db
def test_relogin_error(
    app,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_nonce():
        raise Exception()

    monkeypatch.setattr("ami.authentication.views.generate_nonce", fake_nonce)
    response = app.get("/relogin-france-connect")
    redirected_url = response.headers["location"]
    assert redirected_url == "https://localhost:5173/#/technical-error"
