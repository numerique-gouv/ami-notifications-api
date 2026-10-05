import urllib.parse

import pytest

from ami.authentication.auth import decode_jwt_token
from ami.authentication.models import Nonce, RevokedAuthToken
from ami.tests.utils import assert_query_fails_without_auth, login, url_contains_param
from ami.user.models import User


@pytest.mark.django_db
def test_logout(
    settings,
    app,
    user: User,
) -> None:
    login(app, user)
    token = decode_jwt_token(
        app.cookies[settings.AUTH_COOKIE_JWT_NAME].split(" ")[1].replace('"', "")
    )
    assert token
    response = app.post("/logout")
    assert response.status_code == 201
    assert not response.client.cookies.get(settings.AUTH_COOKIE_JWT_NAME)
    assert not response.client.cookies.get(settings.USERINFO_COOKIE_NAME)
    assert RevokedAuthToken.objects.count() == 1
    revoked_auth_token = RevokedAuthToken.objects.get()
    assert revoked_auth_token.jti == token["jti"]


@pytest.mark.django_db
def test_logout_without_auth(
    app,
) -> None:
    assert_query_fails_without_auth(app, "/logout", method="post")


@pytest.mark.parametrize("fc_mode", ["noproxy", "proxy"])
@pytest.mark.django_db
def test_logout_france_connect(
    fc_mode,
    settings,
    app,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    if fc_mode == "noproxy":
        settings.PUBLIC_FC_PROXY_BASE_URL = ""
    else:
        settings.PUBLIC_FC_PROXY_BASE_URL = "https://fake-fc-proxy"

    FAKE_NONCE = "some-random-nonce"
    monkeypatch.setattr("ami.authentication.views.generate_nonce", lambda: FAKE_NONCE)

    response = app.get("/logout-france-connect")
    assert response.status_code == 302
    redirected_url = response.headers["location"]
    parsed = urllib.parse.urlparse(redirected_url)
    assert parsed.path == "/api/v2/session/end"  # FC Logout
    redirected_url_query = urllib.parse.parse_qs(parsed.query)

    if fc_mode == "noproxy":
        # with logout-callback as return uri, and a state
        assert url_contains_param(
            "post_logout_redirect_uri", "https://localhost:5173/logout-callback", redirected_url
        )
        nonce = Nonce.objects.get(id=redirected_url_query["state"][0])
    else:
        assert url_contains_param(
            "post_logout_redirect_uri", settings.PUBLIC_FC_PROXY_BASE_URL, redirected_url
        )
        proxy_state_url = redirected_url_query["state"][0]
        assert proxy_state_url.startswith("https://localhost:5173/logout-callback?")
        parsed_proxy_state_url_query = urllib.parse.parse_qs(
            urllib.parse.urlparse(proxy_state_url).query
        )
        nonce = Nonce.objects.get(id=parsed_proxy_state_url_query["state"][0])

    assert nonce.context is None
