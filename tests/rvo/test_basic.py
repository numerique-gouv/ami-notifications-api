from urllib.parse import urlencode

import pytest
from litestar import Litestar
from litestar.testing import TestClient
from pytest_httpx import HTTPXMock

from app import env
from tests.base import ConnectedTestClient
from tests.utils import url_contains_param

from .utils import check_url_when_logged_out


async def test_login_france_connect(
    test_client: TestClient[Litestar],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    FAKE_NONCE = "some-random-nonce"
    monkeypatch.setattr("app.generate_nonce", lambda: FAKE_NONCE)
    response = test_client.get("/rvo/login-france-connect", follow_redirects=False)
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
        "redirect_uri",
        env.PUBLIC_FC_PROXY or env.PUBLIC_FC_SERVICE_PROVIDER_REDIRECT_URL,
        redirected_url,
    )
    assert url_contains_param("response_type", "code", redirected_url)
    assert url_contains_param("client_id", env.PUBLIC_FC_SERVICE_PROVIDER_CLIENT_ID, redirected_url)
    assert url_contains_param("state", env.PUBLIC_FC_SERVICE_PROVIDER_REDIRECT_URL, redirected_url)
    assert url_contains_param("nonce", FAKE_NONCE, redirected_url)
    assert url_contains_param("acr_values", "eidas1", redirected_url)
    assert url_contains_param("prompt", "login", redirected_url)


async def test_rvo_login_callback(
    test_client: TestClient[Litestar],
    httpx_mock: HTTPXMock,
    jwt_encoded_userinfo: str,
) -> None:
    # The following fake id_token corresponds to the following decoded id_token:
    #  {'sub': 'cff67ebe00792a2f2b5115dcc1a65d115adb3b73653fb3ed1b88ea11a7a2589av1',
    #   'auth_time': 1763455959,
    #   'acr': 'eidas1',
    #   'nonce': 'YTc3NzZlNjUtNmY3OC00YzExLThmODItMTg0MDg2ZjQ0YzEyLTIwMjUtMTEtMTggMDg6NTI6MzUuNjM1OTYyKzAwOjAw',
    #   'aud': '33fe498cc172fe691778912a2967baa650b24f1ae0ebbe47ae552f37b2d25ead',
    #   'exp': 1763456019,
    #   'iat': 1763455959,
    #   'iss': 'https://fcp-low.sbx.dev-franceconnect.fr/api/v2'}

    NONCE = "YTc3NzZlNjUtNmY3OC00YzExLThmODItMTg0MDg2ZjQ0YzEyLTIwMjUtMTEtMTggMDg6NTI6MzUuNjM1OTYyKzAwOjAw"
    STATE = "some random state"

    fake_id_token = "eyJhbGciOiJFUzI1NiIsImtpZCI6InBrY3MxMTpFUzI1Njpoc20ifQ.eyJzdWIiOiJjZmY2N2ViZTAwNzkyYTJmMmI1MTE1ZGNjMWE2NWQxMTVhZGIzYjczNjUzZmIzZWQxYjg4ZWExMWE3YTI1ODlhdjEiLCJhdXRoX3RpbWUiOjE3NjM0NTU5NTksImFjciI6ImVpZGFzMSIsIm5vbmNlIjoiWVRjM056WmxOalV0Tm1ZM09DMDBZekV4TFRobU9ESXRNVGcwTURnMlpqUTBZekV5TFRJd01qVXRNVEV0TVRnZ01EZzZOVEk2TXpVdU5qTTFPVFl5S3pBd09qQXciLCJhdWQiOiIzM2ZlNDk4Y2MxNzJmZTY5MTc3ODkxMmEyOTY3YmFhNjUwYjI0ZjFhZTBlYmJlNDdhZTU1MmYzN2IyZDI1ZWFkIiwiZXhwIjoxNzYzNDU2MDE5LCJpYXQiOjE3NjM0NTU5NTksImlzcyI6Imh0dHBzOi8vZmNwLWxvdy5zYnguZGV2LWZyYW5jZWNvbm5lY3QuZnIvYXBpL3YyIn0.ynJnN7WY9hN9ACp27ETHg9pDA6tje09MlAfkkADcP6R5Ro_pLpQJ6Jtt4T3zn4ERMC2HKBkGSy1UcZgvLNPSFQ"

    fake_token_json_response = {
        "access_token": "fake access token",
        "expires_in": 60,
        "id_token": fake_id_token,
        "scope": "openid given_name family_name preferred_username birthdate gender birthplace birthcountry email",
        "token_type": "Bearer",
    }
    httpx_mock.add_response(
        method="POST",
        url="https://fcp-low.sbx.dev-franceconnect.fr/api/v2/token",
        json=fake_token_json_response,
    )
    httpx_mock.add_response(
        method="GET", url="https://fcp-low.sbx.dev-franceconnect.fr/api/v2/jwks"
    )
    httpx_mock.add_response(
        method="GET",
        url="https://fcp-low.sbx.dev-franceconnect.fr/api/v2/userinfo",
        json=jwt_encoded_userinfo,
    )

    test_client.set_session_data({"nonce": NONCE, "state": STATE})
    response = test_client.get(f"/rvo/login-callback?code=fake-code&state={STATE}")

    assert response.status_code == 200
    assert "error" not in str(response.url)
    assert test_client.get_session_data()["id_token"] == fake_id_token
    assert test_client.get_session_data()["userinfo"]["given_name"] == "Angela Claire Louise"
    assert "nonce" not in test_client.get_session_data()
    assert "state" not in test_client.get_session_data()


async def test_rvo_login_callback_token_query_failure(
    test_client: TestClient[Litestar],
    httpx_mock: HTTPXMock,
) -> None:
    NONCE = "YTc3NzZlNjUtNmY3OC00YzExLThmODItMTg0MDg2ZjQ0YzEyLTIwMjUtMTEtMTggMDg6NTI6MzUuNjM1OTYyKzAwOjAw"
    STATE = "some random state"

    token_failure_response = {
        "error": "invalid_grant",
        "error_description": " grant request is invalid (authorization code not found)",
        "error_uri": "https://docs.partenaires.franceconnect.gouv.fr/fs/fs-technique/fs-technique-erreurs/?code=Y049E20B&id=801d508c-72d7-459d-8947-104cf89ce015",
    }
    httpx_mock.add_response(
        method="POST",
        url="https://fcp-low.sbx.dev-franceconnect.fr/api/v2/token",
        json=token_failure_response,
        status_code=401,
    )

    test_client.set_session_data({"nonce": NONCE, "state": STATE})
    response = test_client.get(f"/rvo/login-callback?code=fake-code&state={STATE}")

    assert response.status_code == 401
    assert "error" in str(response.text)
    assert "client_secret" not in str(response.text)


async def test_rvo_login_callback_bad_nonce(
    test_client: TestClient[Litestar],
    httpx_mock: HTTPXMock,
) -> None:
    # The following fake id_token corresponds to the following decoded id_token:
    #  {'sub': 'cff67ebe00792a2f2b5115dcc1a65d115adb3b73653fb3ed1b88ea11a7a2589av1',
    #   'auth_time': 1763455959,
    #   'acr': 'eidas1',
    #   'nonce': 'YTc3NzZlNjUtNmY3OC00YzExLThmODItMTg0MDg2ZjQ0YzEyLTIwMjUtMTEtMTggMDg6NTI6MzUuNjM1OTYyKzAwOjAw',
    #   'aud': '33fe498cc172fe691778912a2967baa650b24f1ae0ebbe47ae552f37b2d25ead',
    #   'exp': 1763456019,
    #   'iat': 1763455959,
    #   'iss': 'https://fcp-low.sbx.dev-franceconnect.fr/api/v2'}

    fake_id_token = "eyJhbGciOiJFUzI1NiIsImtpZCI6InBrY3MxMTpFUzI1Njpoc20ifQ.eyJzdWIiOiJjZmY2N2ViZTAwNzkyYTJmMmI1MTE1ZGNjMWE2NWQxMTVhZGIzYjczNjUzZmIzZWQxYjg4ZWExMWE3YTI1ODlhdjEiLCJhdXRoX3RpbWUiOjE3NjM0NTU5NTksImFjciI6ImVpZGFzMSIsIm5vbmNlIjoiWVRjM056WmxOalV0Tm1ZM09DMDBZekV4TFRobU9ESXRNVGcwTURnMlpqUTBZekV5TFRJd01qVXRNVEV0TVRnZ01EZzZOVEk2TXpVdU5qTTFPVFl5S3pBd09qQXciLCJhdWQiOiIzM2ZlNDk4Y2MxNzJmZTY5MTc3ODkxMmEyOTY3YmFhNjUwYjI0ZjFhZTBlYmJlNDdhZTU1MmYzN2IyZDI1ZWFkIiwiZXhwIjoxNzYzNDU2MDE5LCJpYXQiOjE3NjM0NTU5NTksImlzcyI6Imh0dHBzOi8vZmNwLWxvdy5zYnguZGV2LWZyYW5jZWNvbm5lY3QuZnIvYXBpL3YyIn0.ynJnN7WY9hN9ACp27ETHg9pDA6tje09MlAfkkADcP6R5Ro_pLpQJ6Jtt4T3zn4ERMC2HKBkGSy1UcZgvLNPSFQ"

    fake_token_json_response = {
        "access_token": "fake access token",
        "expires_in": 60,
        "id_token": fake_id_token,
        "scope": "openid given_name family_name preferred_username birthdate gender birthplace birthcountry email",
        "token_type": "Bearer",
    }
    httpx_mock.add_response(
        method="POST",
        url="https://fcp-low.sbx.dev-franceconnect.fr/api/v2/token",
        json=fake_token_json_response,
    )

    STATE = "some random state"
    test_client.set_session_data({"nonce": "some other nonce", "state": STATE})
    response = test_client.get(f"/rvo/login-callback?code=fake-code&state={STATE}")

    assert response.status_code == 200
    assert (
        response.url
        == "http://testserver.local/rvo?error=Erreur+lors+de+la+France+Connexion&error_description=Veuillez+r%C3%A9essayer+plus+tard."
    )


async def test_login_callback_bad_state(
    test_client: TestClient[Litestar],
) -> None:
    STATE = "some random state"
    test_client.set_session_data({"nonce": "some other nonce", "state": "some other state"})
    response = test_client.get(
        f"/rvo/login-callback?code=fake-code&state={STATE}", follow_redirects=False
    )

    assert response.status_code == 302
    redirected_url = response.headers["location"]
    assert (
        redirected_url
        == "/rvo?error=Erreur+lors+de+la+France+Connexion&error_description=Veuillez+r%C3%A9essayer+plus+tard."
    )


async def test_login_callback_user_aborted(
    test_client: TestClient[Litestar],
) -> None:
    test_client.set_session_data({"nonce": "some other nonce", "state": "some other state"})
    response = test_client.get(
        "/rvo/login-callback?error=access_denied&error_description=User auth aborted&state=some state",
        follow_redirects=False,
    )

    assert response.status_code == 302
    redirected_url = response.headers["location"]
    assert redirected_url == "/rvo"


async def test_rvo_logout(
    connected_test_client: ConnectedTestClient,
) -> None:
    data: dict[str, str] = {
        "id_token_hint": "fake id token",
        "state": "https://localhost:8000/rvo/logged_out",
        "post_logout_redirect_uri": "https://ami-fc-proxy-dev.osc-fr1.scalingo.io/",
    }
    params: str = urlencode(data)
    url: str = f"https://fcp-low.sbx.dev-franceconnect.fr/api/v2/session/end?{params}"

    response = connected_test_client.get("/rvo/logout", follow_redirects=False)
    assert response.status_code == 302
    assert response.headers["location"] == url
    # Session has been removed, previously to redirecting to FC logout URL.
    assert connected_test_client.get_session_data() == {}


async def test_rvo_home_when_logged_in(
    connected_test_client: ConnectedTestClient,
) -> None:
    response = connected_test_client.get("/rvo", follow_redirects=False)
    assert response.status_code == 200
    assert "/rvo/detail/1" in response.text
    assert "/rvo/detail/2" in response.text


async def test_rvo_detail_when_logged_in(
    connected_test_client: ConnectedTestClient,
) -> None:
    response = connected_test_client.get("/rvo/detail/1", follow_redirects=False)
    assert "Rendez-vous dans votre Agence France Travail Paris 18e Ney" in response.text
    assert response.status_code == 200
    assert "Annuler le RDV" in response.text

    response = connected_test_client.get("/rvo/detail/2", follow_redirects=False)
    assert "Rendez-vous dans votre Maison France Services" in response.text
    assert response.status_code == 200
    assert "Annuler le RDV" in response.text


async def test_rvo_detail_when_logged_out(
    test_client: TestClient[Litestar],
) -> None:
    await check_url_when_logged_out("/rvo/detail/1", test_client)
