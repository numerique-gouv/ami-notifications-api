import datetime
import json
from base64 import urlsafe_b64encode
from typing import Any

import pytest
from litestar import Litestar
from litestar.testing import TestClient
from pytest_httpx import HTTPXMock
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app import env
from app.auth import generate_nonce, jwt_cookie_auth
from app.models import Nonce, ScheduledNotification, User
from app.utils import build_fc_hash
from tests.ami.utils import assert_query_fails_without_auth, login
from tests.utils import url_contains_param


async def test_generate_nonce(monkeypatch: pytest.MonkeyPatch) -> None:
    FAKE_TIME = datetime.datetime(2020, 12, 25, 17, 5, 55)
    FAKE_UUID = "fake-uuid"

    class mock_datetime(datetime.datetime):
        @classmethod
        def now(cls, tz: datetime.tzinfo | None = datetime.timezone.utc):
            return FAKE_TIME

    monkeypatch.setattr("app.auth.uuid4", lambda: FAKE_UUID)
    monkeypatch.setattr("app.auth.datetime.datetime", mock_datetime)
    assert generate_nonce() == urlsafe_b64encode(f"{FAKE_UUID}-{FAKE_TIME}".encode("utf8")).decode(
        "utf8"
    )


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
        "openid identite_pivot preferred_username email cnaf_quotient_familial",
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
    assert url_contains_param("idp_hint", env.PUBLIC_FC_AMI_IDP_HINT, redirected_url)


async def test_login_callback(
    test_client: TestClient[Litestar],
    db_session: AsyncSession,
    httpx_mock: HTTPXMock,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    NONCE = "YTc3NzZlNjUtNmY3OC00YzExLThmODItMTg0MDg2ZjQ0YzEyLTIwMjUtMTEtMTggMDg6NTI6MzUuNjM1OTYyKzAwOjAw"
    nonce = Nonce(nonce=NONCE)
    db_session.add(nonce)
    await db_session.commit()

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
    monkeypatch.setattr("app.env.FC_AMI_CLIENT_SECRET", "fake-client-secret")

    response = test_client.get(
        f"/login-callback?code=fake-code&state={nonce.id}", follow_redirects=False
    )

    assert response.status_code == 302
    redirected_url = response.headers["location"]
    assert redirected_url.startswith("https://localhost:5173")
    assert "access_token" in redirected_url
    assert "scope" in redirected_url
    assert "id_token" in redirected_url
    assert "token_type" in redirected_url
    assert "is_logged_in" in redirected_url
    all_nonces = (await db_session.execute(select(Nonce))).scalars().all()
    assert len(all_nonces) == 0


async def test_login_callback_token_query_failure(
    test_client: TestClient[Litestar],
    db_session: AsyncSession,
    httpx_mock: HTTPXMock,
) -> None:
    NONCE = "some random nonce"
    nonce = Nonce(nonce=NONCE)
    db_session.add(nonce)
    await db_session.commit()

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

    response = test_client.get(
        f"/login-callback?code=fake-code&state={nonce.id}", follow_redirects=False
    )

    assert response.status_code == 302
    redirected_url = response.headers["location"]
    assert (
        redirected_url
        == "https://localhost:5173/?error=Erreur+lors+de+la+FranceConnexion%2C+veuillez+r%C3%A9essayer+plus+tard.&error_type=FranceConnect"
    )


async def test_login_callback_bad_state(
    test_client: TestClient[Litestar],
    db_session: AsyncSession,
) -> None:
    NONCE = "some random nonce"
    nonce = Nonce(nonce=NONCE)
    db_session.add(nonce)
    await db_session.commit()

    response = test_client.get("/login-callback?code=fake-code&state=", follow_redirects=False)
    assert response.status_code == 302
    redirected_url = response.headers["location"]
    assert url_contains_param("error_type", "FranceConnect", redirected_url)
    assert url_contains_param(
        "error", "Erreur lors de la FranceConnexion, veuillez réessayer plus tard.", redirected_url
    )
    assert url_contains_param("code", "missing_state", redirected_url)

    response = test_client.get(
        "/login-callback?code=fake-code&state=some-other-state", follow_redirects=False
    )
    assert response.status_code == 302
    redirected_url = response.headers["location"]
    assert url_contains_param("error_type", "FranceConnect", redirected_url)
    assert url_contains_param(
        "error", "Erreur lors de la FranceConnexion, veuillez réessayer plus tard.", redirected_url
    )
    assert url_contains_param("code", "invalid_state", redirected_url)

    response = test_client.get(
        "/login-callback?code=fake-code&state={uuid.uuid4()}", follow_redirects=False
    )
    assert response.status_code == 302
    redirected_url = response.headers["location"]
    assert url_contains_param("error_type", "FranceConnect", redirected_url)
    assert url_contains_param(
        "error", "Erreur lors de la FranceConnexion, veuillez réessayer plus tard.", redirected_url
    )
    assert url_contains_param("code", "invalid_state", redirected_url)


async def test_login_callback_bad_nonce(
    test_client: TestClient[Litestar],
    db_session: AsyncSession,
    httpx_mock: HTTPXMock,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    NONCE = "some random nonce"
    nonce = Nonce(nonce=NONCE)
    db_session.add(nonce)
    await db_session.commit()

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
    monkeypatch.setattr("app.env.FC_AMI_CLIENT_SECRET", "fake-client-secret")

    response = test_client.get(
        f"/login-callback?code=fake-code&state={nonce.id}", follow_redirects=False
    )

    assert response.status_code == 302
    redirected_url = response.headers["location"]
    assert url_contains_param("error_type", "FranceConnect", redirected_url)
    assert url_contains_param(
        "error", "Erreur lors de la FranceConnexion, veuillez réessayer plus tard.", redirected_url
    )
    assert url_contains_param("code", "invalid_nonce", redirected_url)
    all_nonces = (await db_session.execute(select(Nonce))).scalars().all()
    assert len(all_nonces) == 0


async def test_login_callback_fc_error(
    test_client: TestClient[Litestar],
) -> None:
    response = test_client.get(
        "/login-callback?error=access_denied&error_description=User+auth+aborted&state=some-state",
        follow_redirects=False,
    )

    assert response.status_code == 302
    redirected_url = response.headers["location"]
    assert url_contains_param("error_type", "FranceConnect", redirected_url)
    assert url_contains_param("error", "access_denied", redirected_url)
    assert url_contains_param("error_description", "User auth aborted", redirected_url)
    assert url_contains_param("code", "fc_error", redirected_url)


async def test_fc_get_userinfo(
    test_client: TestClient[Litestar],
    db_session: AsyncSession,
    httpx_mock: HTTPXMock,
    monkeypatch: pytest.MonkeyPatch,
    userinfo: dict[str, Any],
) -> None:
    fake_userinfo_token = "fake userinfo jwt token"
    auth = {"authorization": "Bearer foobar_access_token"}
    httpx_mock.add_response(
        method="GET",
        url="https://fcp-low.sbx.dev-franceconnect.fr/api/v2/userinfo",
        match_headers=auth,
        text=fake_userinfo_token,
        is_reusable=True,
    )

    def fake_jwt_decode(*args: Any, **params: Any):
        return userinfo

    monkeypatch.setattr("jwt.decode", fake_jwt_decode)

    response = test_client.get("/fc_userinfo", headers=auth)

    assert response.status_code == 200
    all_users = (await db_session.execute(select(User))).scalars().all()
    assert len(all_users) == 1
    user = all_users[0]
    assert json.loads(response.text) == {
        "user_id": str(user.id),
        "user_data": fake_userinfo_token,
    }

    assert user.fc_hash == "4abd71ec1f581dce2ea2221cbeac7c973c6aea7bcb835acdfe7d6494f1528060"
    assert user.already_seen is True

    all_scheduled_notifications = (
        (await db_session.execute(select(ScheduledNotification))).scalars().all()
    )
    assert len(all_scheduled_notifications) == 1
    scheduled_notification = all_scheduled_notifications[0]
    assert scheduled_notification.user.id == user.id
    assert scheduled_notification.content_title == "Bienvenue sur AMI 👋"
    assert (
        scheduled_notification.content_body
        == "Recevez des rappels sur votre situation et suivez vos démarches en cours depuis l'application."
    )
    assert scheduled_notification.content_icon == "fr-icon-information-line"
    assert scheduled_notification.reference == "ami:welcome"
    assert scheduled_notification.scheduled_at < datetime.datetime.now(datetime.timezone.utc)
    assert scheduled_notification.sender == "AMI"
    assert scheduled_notification.sent_at is None

    response = test_client.get("/fc_userinfo", headers=auth)

    assert response.status_code == 200
    assert json.loads(response.text) == {
        "user_id": str(user.id),
        "user_data": fake_userinfo_token,
    }
    assert "authorization" in response.headers
    assert "set-cookie" in response.headers
    assert response.cookies.get(jwt_cookie_auth.key)

    all_scheduled_notifications = (
        (await db_session.execute(select(ScheduledNotification))).scalars().all()
    )
    assert len(all_scheduled_notifications) == 1


async def test_fc_get_userinfo_user_never_seen(
    test_client: TestClient[Litestar],
    db_session: AsyncSession,
    httpx_mock: HTTPXMock,
    monkeypatch: pytest.MonkeyPatch,
    userinfo: dict[str, Any],
) -> None:
    fake_userinfo_token = "fake userinfo jwt token"
    auth = {"authorization": "Bearer foobar_access_token"}
    httpx_mock.add_response(
        method="GET",
        url="https://fcp-low.sbx.dev-franceconnect.fr/api/v2/userinfo",
        match_headers=auth,
        text=fake_userinfo_token,
        is_reusable=True,
    )

    fc_hash = build_fc_hash(
        given_name=userinfo["given_name"],
        family_name=userinfo["family_name"],
        birthdate=userinfo["birthdate"],
        gender=userinfo["gender"],
        birthplace=userinfo["birthplace"],
        birthcountry=userinfo["birthcountry"],
    )
    user = User(fc_hash=fc_hash, already_seen=False)
    db_session.add(user)
    await db_session.commit()

    def fake_jwt_decode(*args: Any, **params: Any):
        return userinfo

    monkeypatch.setattr("jwt.decode", fake_jwt_decode)

    response = test_client.get("/fc_userinfo", headers=auth)

    assert response.status_code == 200
    all_users = (await db_session.execute(select(User))).scalars().all()
    assert len(all_users) == 1
    assert all_users[0].id == user.id
    await db_session.refresh(user)
    assert json.loads(response.text) == {
        "user_id": str(user.id),
        "user_data": fake_userinfo_token,
    }

    assert user.fc_hash == "4abd71ec1f581dce2ea2221cbeac7c973c6aea7bcb835acdfe7d6494f1528060"
    assert user.already_seen is True

    all_scheduled_notifications = (
        (await db_session.execute(select(ScheduledNotification))).scalars().all()
    )
    assert len(all_scheduled_notifications) == 1
    scheduled_notification = all_scheduled_notifications[0]
    assert scheduled_notification.user.id == user.id
    assert scheduled_notification.content_title == "Bienvenue sur AMI 👋"
    assert (
        scheduled_notification.content_body
        == "Recevez des rappels sur votre situation et suivez vos démarches en cours depuis l'application."
    )
    assert scheduled_notification.content_icon == "fr-icon-information-line"
    assert scheduled_notification.reference == "ami:welcome"
    assert scheduled_notification.scheduled_at < datetime.datetime.now(datetime.timezone.utc)
    assert scheduled_notification.sender == "AMI"
    assert scheduled_notification.sent_at is None

    # again, if notification reference already exists
    user.already_seen = False
    db_session.add(user)
    await db_session.commit()
    response = test_client.get("/fc_userinfo", headers=auth)
    assert response.status_code == 200
    all_scheduled_notifications = (
        (await db_session.execute(select(ScheduledNotification))).scalars().all()
    )
    assert len(all_scheduled_notifications) == 1


async def test_logout(
    user: User,
    test_client: TestClient[Litestar],
) -> None:
    login(user, test_client)
    assert test_client.cookies.get(jwt_cookie_auth.key)
    response = test_client.post("/logout")
    assert response.status_code == 201
    assert not response.cookies.get(jwt_cookie_auth.key)


async def test_logout_without_auth(
    test_client: TestClient[Litestar],
) -> None:
    await assert_query_fails_without_auth("/logout", test_client, method="post")


async def test_check_auth(
    user: User,
    test_client: TestClient[Litestar],
) -> None:
    login(user, test_client)
    response = test_client.get("/check-auth")
    assert response.status_code == 200
    assert response.json() == {"authenticated": True}


async def test_check_auth_without_auth(
    test_client: TestClient[Litestar],
) -> None:
    await assert_query_fails_without_auth("/check-auth", test_client)
