import pytest
from litestar import Litestar
from litestar.testing import TestClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app import env
from app.models import Nonce
from tests.utils import url_contains_param


async def test_login_france_connect(
    test_client: TestClient[Litestar],
    db_session: AsyncSession,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    FAKE_NONCE = "some-random-nonce"
    monkeypatch.setattr("app.controllers.auth.generate_nonce", lambda: FAKE_NONCE)
    response = test_client.get("/login-france-connect", follow_redirects=False)
    redirected_url = response.headers["location"]
    all_nonces = (await db_session.execute(select(Nonce))).scalars().all()
    assert len(all_nonces) == 1
    nonce = all_nonces[0]
    assert nonce.nonce == FAKE_NONCE
    assert response.status_code == 302
    redirected_url = response.headers["location"]
    assert redirected_url.startswith(
        f"{env.PUBLIC_FC_BASE_URL}{env.PUBLIC_FC_AUTHORIZATION_ENDPOINT}"
    )
    assert url_contains_param(
        "scope",
        "openid identite_pivot preferred_username email",
        redirected_url,
    )
    assert url_contains_param(
        "redirect_uri", env.PUBLIC_FC_PROXY or env.PUBLIC_FC_AMI_REDIRECT_URL, redirected_url
    )
    assert url_contains_param("response_type", "code", redirected_url)
    assert url_contains_param("client_id", env.PUBLIC_FC_AMI_CLIENT_ID, redirected_url)
    assert url_contains_param(
        "state", f"{env.PUBLIC_FC_AMI_REDIRECT_URL}?state={nonce.id}", redirected_url
    )
    assert url_contains_param("nonce", nonce.nonce, redirected_url)
    assert url_contains_param("acr_values", "eidas1", redirected_url)
    assert url_contains_param("prompt", "login", redirected_url)


async def test_login_france_connect_error(
    test_client: TestClient[Litestar],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_nonce():
        raise Exception()

    monkeypatch.setattr("app.controllers.auth.generate_nonce", fake_nonce)
    response = test_client.get("/login-france-connect", follow_redirects=False)
    redirected_url = response.headers["location"]
    assert redirected_url == "https://localhost:5173/#/technical-error"
