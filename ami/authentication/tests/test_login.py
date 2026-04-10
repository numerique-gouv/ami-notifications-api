import pytest

from ami.authentication.models import Nonce
from ami.tests.utils import url_contains_param


@pytest.mark.django_db
def test_login_france_connect(
    settings,
    django_app,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    FAKE_NONCE = "some-random-nonce"
    monkeypatch.setattr("ami.authentication.views.generate_nonce", lambda: FAKE_NONCE)
    response = django_app.get("/login-france-connect")
    redirected_url = response.headers["location"]
    assert Nonce.objects.count() == 1
    nonce = Nonce.objects.get()
    assert nonce.nonce == FAKE_NONCE
    assert response.status_code == 302
    redirected_url = response.headers["location"]
    assert redirected_url.startswith(
        f"{settings.PUBLIC_FC_BASE_URL}{settings.FC_AUTHORIZATION_ENDPOINT}"
    )
    assert url_contains_param(
        "scope",
        "openid identite_pivot preferred_username email",
        redirected_url,
    )
    assert url_contains_param(
        "redirect_uri",
        settings.PUBLIC_FC_PROXY or settings.FC_AMI_REDIRECT_URL,
        redirected_url,
    )
    assert url_contains_param("response_type", "code", redirected_url)
    assert url_contains_param("client_id", settings.FC_AMI_CLIENT_ID, redirected_url)
    assert url_contains_param(
        "state", f"{settings.FC_AMI_REDIRECT_URL}?state={nonce.id}", redirected_url
    )
    assert url_contains_param("nonce", nonce.nonce, redirected_url)
    assert url_contains_param("acr_values", "eidas1", redirected_url)
    assert url_contains_param("prompt", "login", redirected_url)


def test_login_france_connect_error(
    django_app,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_nonce():
        raise Exception()

    monkeypatch.setattr("ami.authentication.views.generate_nonce", fake_nonce)
    response = django_app.get("/login-france-connect")
    redirected_url = response.headers["location"]
    assert redirected_url == "https://localhost:5173/technical-error"
