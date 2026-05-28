from urllib.parse import parse_qs, urlparse

import pytest

from ami.authentication.models import Nonce
from ami.tests.utils import url_contains_param


@pytest.mark.django_db
def test_login_ami_fi(
    settings,
    app,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    settings.PUBLIC_FC_PROXY_BASE_URL = "https://ami-fc-proxy-dev.osc-fr1.scalingo.io"
    FAKE_NONCE = "some-random-nonce"
    monkeypatch.setattr("ami.authentication.views.generate_nonce", lambda: FAKE_NONCE)
    response = app.get("/login-ami-fi")
    assert Nonce.objects.count() == 1
    nonce = Nonce.objects.get()
    assert nonce.nonce == FAKE_NONCE
    assert nonce.context == {
        "idp": "ami-fi",
        "provider_ids": [],
    }
    assert response.status_code == 302
    redirected_url = response.headers["location"]
    assert redirected_url.startswith(
        f"{settings.PUBLIC_FC_PROXY_BASE_URL}/ami-fi-authorize-request/"
    )
    assert url_contains_param(
        "from_url",
        "https://localhost:8000/",
        redirected_url,
    )
    parsed = urlparse(redirected_url)
    redirected_url_query = parse_qs(parsed.query)
    fc_url = redirected_url_query["fc_url"][0]
    assert url_contains_param(
        "scope",
        "openid identite_pivot preferred_username email",
        fc_url,
    )
    assert url_contains_param(
        "redirect_uri",
        f"{settings.PUBLIC_FC_PROXY_BASE_URL}/",
        fc_url,
    )
    assert url_contains_param("response_type", "code", fc_url)
    assert url_contains_param("client_id", settings.FC_AMI_CLIENT_ID, fc_url)
    assert url_contains_param("state", f"{settings.FC_AMI_REDIRECT_URL}?state=", fc_url)
    assert url_contains_param("nonce", nonce.nonce, fc_url)
    assert url_contains_param("acr_values", "eidas1", fc_url)
    assert url_contains_param("prompt", "login", fc_url)
    assert url_contains_param("idp_hint", settings.FI_IDP_ID, fc_url)
    parsed = urlparse(fc_url)
    fc_url_query = parse_qs(parsed.query)
    state = fc_url_query["state"][0]
    state = state.replace(f"{settings.FC_AMI_REDIRECT_URL}?state=", "")


@pytest.mark.django_db
def test_login_ami_fi_quotient(
    settings,
    app,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    settings.PUBLIC_FC_PROXY_BASE_URL = "https://ami-fc-proxy-dev.osc-fr1.scalingo.io"
    FAKE_NONCE = "some-random-nonce"
    monkeypatch.setattr("ami.authentication.views.generate_nonce", lambda: FAKE_NONCE)
    response = app.get("/login-ami-fi?provider_id=api_particulier_quotient")
    assert Nonce.objects.count() == 1
    nonce = Nonce.objects.get()
    assert nonce.nonce == FAKE_NONCE
    assert nonce.context == {
        "idp": "ami-fi",
        "provider_ids": ["api_particulier_quotient"],
    }
    assert response.status_code == 302
    redirected_url = response.headers["location"]
    assert redirected_url.startswith(
        f"{settings.PUBLIC_FC_PROXY_BASE_URL}/ami-fi-authorize-request/"
    )
    assert url_contains_param(
        "from_url",
        "https://localhost:8000/",
        redirected_url,
    )
    parsed = urlparse(redirected_url)
    redirected_url_query = parse_qs(parsed.query)
    fc_url = redirected_url_query["fc_url"][0]
    assert url_contains_param(
        "scope",
        "openid identite_pivot preferred_username email",
        fc_url,
    )
    assert url_contains_param(
        "redirect_uri",
        f"{settings.PUBLIC_FC_PROXY_BASE_URL}/",
        fc_url,
    )
    assert url_contains_param("response_type", "code", fc_url)
    assert url_contains_param("client_id", settings.FC_AMI_CLIENT_ID, fc_url)
    assert url_contains_param("state", f"{settings.FC_AMI_REDIRECT_URL}?state=", fc_url)
    assert url_contains_param("nonce", nonce.nonce, fc_url)
    assert url_contains_param("acr_values", "eidas1", fc_url)
    assert url_contains_param("prompt", "login", fc_url)
    assert url_contains_param("idp_hint", settings.FI_IDP_ID, fc_url)
    parsed = urlparse(fc_url)
    fc_url_query = parse_qs(parsed.query)
    state = fc_url_query["state"][0]
    state = state.replace(f"{settings.FC_AMI_REDIRECT_URL}?state=", "")


@pytest.mark.django_db
def test_login_ami_fi_statut_etudiant(
    settings,
    app,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    settings.PUBLIC_FC_PROXY_BASE_URL = "https://ami-fc-proxy-dev.osc-fr1.scalingo.io"
    FAKE_NONCE = "some-random-nonce"
    monkeypatch.setattr("ami.authentication.views.generate_nonce", lambda: FAKE_NONCE)
    response = app.get("/login-ami-fi?provider_id=api_particulier_statut_etudiant")
    assert Nonce.objects.count() == 1
    nonce = Nonce.objects.get()
    assert nonce.nonce == FAKE_NONCE
    assert nonce.context == {
        "idp": "ami-fi",
        "provider_ids": ["api_particulier_statut_etudiant"],
    }
    assert response.status_code == 302
    redirected_url = response.headers["location"]
    assert redirected_url.startswith(
        f"{settings.PUBLIC_FC_PROXY_BASE_URL}/ami-fi-authorize-request/"
    )
    assert url_contains_param(
        "from_url",
        "https://localhost:8000/",
        redirected_url,
    )
    parsed = urlparse(redirected_url)
    redirected_url_query = parse_qs(parsed.query)
    fc_url = redirected_url_query["fc_url"][0]
    assert url_contains_param(
        "scope",
        "openid identite_pivot preferred_username email",
        fc_url,
    )
    assert url_contains_param(
        "redirect_uri",
        f"{settings.PUBLIC_FC_PROXY_BASE_URL}/",
        fc_url,
    )
    assert url_contains_param("response_type", "code", fc_url)
    assert url_contains_param("client_id", settings.FC_AMI_CLIENT_ID, fc_url)
    assert url_contains_param("state", f"{settings.FC_AMI_REDIRECT_URL}?state=", fc_url)
    assert url_contains_param("nonce", nonce.nonce, fc_url)
    assert url_contains_param("acr_values", "eidas1", fc_url)
    assert url_contains_param("prompt", "login", fc_url)
    assert url_contains_param("idp_hint", settings.FI_IDP_ID, fc_url)
    parsed = urlparse(fc_url)
    fc_url_query = parse_qs(parsed.query)
    state = fc_url_query["state"][0]
    state = state.replace(f"{settings.FC_AMI_REDIRECT_URL}?state=", "")


def test_login_ami_fi_error(
    app,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_nonce():
        raise Exception()

    monkeypatch.setattr("ami.authentication.views.generate_nonce", fake_nonce)
    response = app.get("/login-ami-fi")
    redirected_url = response.headers["location"]
    assert redirected_url == "https://localhost:5173/#/technical-error"
