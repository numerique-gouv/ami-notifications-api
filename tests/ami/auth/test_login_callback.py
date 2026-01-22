import datetime
from typing import Any

import pytest
from litestar import Litestar
from litestar.testing import TestClient
from pytest_httpx import HTTPXMock
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app import env
from app.models import Nonce, ScheduledNotification, User
from app.utils import build_fc_hash
from tests.utils import url_contains_param


async def test_login_callback(
    test_client: TestClient[Litestar],
    db_session: AsyncSession,
    httpx_mock: HTTPXMock,
    monkeypatch: pytest.MonkeyPatch,
    userinfo: dict[str, Any],
    decoded_id_token: dict[str, Any],
) -> None:
    def fake_jwt_decode(*args: Any, **params: Any):
        encoded = args[0]
        if encoded == "fake id token":
            return decoded_id_token
        return userinfo

    monkeypatch.setattr("jwt.decode", fake_jwt_decode)
    monkeypatch.setattr("app.controllers.auth.env.FC_AMI_CLIENT_SECRET", "fake-client-secret")
    monkeypatch.setattr(
        "app.controllers.auth.env.PUBLIC_FC_SCOPE",
        env.PUBLIC_FC_SCOPE.replace(" cnaf_quotient_familial", ""),
    )

    NONCE = decoded_id_token["nonce"]
    nonce = Nonce(nonce=NONCE)
    db_session.add(nonce)
    await db_session.commit()

    fake_token_json_response = {
        "access_token": "fake access token",
        "expires_in": 60,
        "id_token": "fake id token",
        "scope": "openid given_name family_name preferred_username birthdate gender birthplace birthcountry email",
        "token_type": "Bearer",
    }
    httpx_mock.add_response(
        method="POST",
        url="https://fcp-low.sbx.dev-franceconnect.fr/api/v2/token",
        json=fake_token_json_response,
    )

    auth = {"authorization": "Bearer fake access token"}
    fake_userinfo_token = "fake userinfo jwt token"
    httpx_mock.add_response(
        method="GET",
        url="https://fcp-low.sbx.dev-franceconnect.fr/api/v2/userinfo",
        match_headers=auth,
        text=fake_userinfo_token,
    )

    response = test_client.get(
        f"/login-callback?code=fake-code&state={nonce.id}", follow_redirects=False
    )

    assert response.status_code == 302
    redirected_url = response.headers["location"]
    assert redirected_url.startswith("https://localhost:5173")
    assert url_contains_param(
        "user_data",
        "fake userinfo jwt token",
        redirected_url,
    )
    assert url_contains_param(
        "user_first_login",
        "true",
        redirected_url,
    )
    assert url_contains_param(
        "user_fc_hash",
        "4abd71ec1f581dce2ea2221cbeac7c973c6aea7bcb835acdfe7d6494f1528060",
        redirected_url,
    )
    assert url_contains_param(
        "is_logged_in",
        "true",
        redirected_url,
    )
    assert "address" not in redirected_url
    all_nonces = (await db_session.execute(select(Nonce))).scalars().all()
    assert len(all_nonces) == 0

    all_users = (await db_session.execute(select(User))).scalars().all()
    assert len(all_users) == 1
    user = all_users[0]

    assert user.fc_hash == "4abd71ec1f581dce2ea2221cbeac7c973c6aea7bcb835acdfe7d6494f1528060"
    assert user.last_logged_in is not None

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


async def test_login_callback_user_already_seen(
    test_client: TestClient[Litestar],
    db_session: AsyncSession,
    httpx_mock: HTTPXMock,
    monkeypatch: pytest.MonkeyPatch,
    userinfo: dict[str, Any],
    decoded_id_token: dict[str, Any],
) -> None:
    def fake_jwt_decode(*args: Any, **params: Any):
        encoded = args[0]
        if encoded == "fake id token":
            return decoded_id_token
        return userinfo

    monkeypatch.setattr("jwt.decode", fake_jwt_decode)
    monkeypatch.setattr("app.controllers.auth.env.FC_AMI_CLIENT_SECRET", "fake-client-secret")
    monkeypatch.setattr(
        "app.controllers.auth.env.PUBLIC_FC_SCOPE",
        env.PUBLIC_FC_SCOPE.replace(" cnaf_quotient_familial", ""),
    )

    NONCE = decoded_id_token["nonce"]
    nonce = Nonce(nonce=NONCE)
    db_session.add(nonce)
    await db_session.commit()

    fake_token_json_response = {
        "access_token": "fake access token",
        "expires_in": 60,
        "id_token": "fake id token",
        "scope": "openid given_name family_name preferred_username birthdate gender birthplace birthcountry email",
        "token_type": "Bearer",
    }
    httpx_mock.add_response(
        method="POST",
        url="https://fcp-low.sbx.dev-franceconnect.fr/api/v2/token",
        json=fake_token_json_response,
    )

    auth = {"authorization": "Bearer fake access token"}
    fake_userinfo_token = "fake userinfo jwt token"
    httpx_mock.add_response(
        method="GET",
        url="https://fcp-low.sbx.dev-franceconnect.fr/api/v2/userinfo",
        match_headers=auth,
        text=fake_userinfo_token,
    )

    fc_hash = build_fc_hash(
        given_name=userinfo["given_name"],
        family_name=userinfo["family_name"],
        birthdate=userinfo["birthdate"],
        gender=userinfo["gender"],
        birthplace=userinfo["birthplace"],
        birthcountry=userinfo["birthcountry"],
    )
    user = User(fc_hash=fc_hash, last_logged_in=datetime.datetime.now(datetime.timezone.utc))
    db_session.add(user)
    await db_session.commit()

    response = test_client.get(
        f"/login-callback?code=fake-code&state={nonce.id}", follow_redirects=False
    )

    assert response.status_code == 302
    redirected_url = response.headers["location"]
    assert redirected_url.startswith("https://localhost:5173")
    assert url_contains_param(
        "user_data",
        "fake userinfo jwt token",
        redirected_url,
    )
    assert url_contains_param(
        "user_first_login",
        "false",
        redirected_url,
    )
    assert url_contains_param(
        "user_fc_hash",
        "4abd71ec1f581dce2ea2221cbeac7c973c6aea7bcb835acdfe7d6494f1528060",
        redirected_url,
    )
    assert url_contains_param(
        "is_logged_in",
        "true",
        redirected_url,
    )
    all_nonces = (await db_session.execute(select(Nonce))).scalars().all()
    assert len(all_nonces) == 0

    all_users = (await db_session.execute(select(User))).scalars().all()
    assert len(all_users) == 1
    user = all_users[0]

    assert user.fc_hash == "4abd71ec1f581dce2ea2221cbeac7c973c6aea7bcb835acdfe7d6494f1528060"
    assert user.last_logged_in is not None

    all_scheduled_notifications = (
        (await db_session.execute(select(ScheduledNotification))).scalars().all()
    )
    assert len(all_scheduled_notifications) == 0


async def test_login_callback_user_never_seen(
    test_client: TestClient[Litestar],
    db_session: AsyncSession,
    httpx_mock: HTTPXMock,
    monkeypatch: pytest.MonkeyPatch,
    userinfo: dict[str, Any],
    decoded_id_token: dict[str, Any],
) -> None:
    def fake_jwt_decode(*args: Any, **params: Any):
        encoded = args[0]
        if encoded == "fake id token":
            return decoded_id_token
        return userinfo

    monkeypatch.setattr("jwt.decode", fake_jwt_decode)
    monkeypatch.setattr("app.controllers.auth.env.FC_AMI_CLIENT_SECRET", "fake-client-secret")
    monkeypatch.setattr(
        "app.controllers.auth.env.PUBLIC_FC_SCOPE",
        env.PUBLIC_FC_SCOPE.replace(" cnaf_quotient_familial", ""),
    )

    NONCE = decoded_id_token["nonce"]
    nonce = Nonce(nonce=NONCE)
    db_session.add(nonce)
    await db_session.commit()

    fake_token_json_response = {
        "access_token": "fake access token",
        "expires_in": 60,
        "id_token": "fake id token",
        "scope": "openid given_name family_name preferred_username birthdate gender birthplace birthcountry email",
        "token_type": "Bearer",
    }
    httpx_mock.add_response(
        method="POST",
        url="https://fcp-low.sbx.dev-franceconnect.fr/api/v2/token",
        json=fake_token_json_response,
    )

    auth = {"authorization": "Bearer fake access token"}
    fake_userinfo_token = "fake userinfo jwt token"
    httpx_mock.add_response(
        method="GET",
        url="https://fcp-low.sbx.dev-franceconnect.fr/api/v2/userinfo",
        match_headers=auth,
        text=fake_userinfo_token,
    )

    fc_hash = build_fc_hash(
        given_name=userinfo["given_name"],
        family_name=userinfo["family_name"],
        birthdate=userinfo["birthdate"],
        gender=userinfo["gender"],
        birthplace=userinfo["birthplace"],
        birthcountry=userinfo["birthcountry"],
    )
    user = User(fc_hash=fc_hash)
    db_session.add(user)
    await db_session.commit()

    response = test_client.get(
        f"/login-callback?code=fake-code&state={nonce.id}", follow_redirects=False
    )

    assert response.status_code == 302
    redirected_url = response.headers["location"]
    assert redirected_url.startswith("https://localhost:5173")
    assert url_contains_param(
        "user_data",
        "fake userinfo jwt token",
        redirected_url,
    )
    assert url_contains_param(
        "user_first_login",
        "true",
        redirected_url,
    )
    assert url_contains_param(
        "user_fc_hash",
        "4abd71ec1f581dce2ea2221cbeac7c973c6aea7bcb835acdfe7d6494f1528060",
        redirected_url,
    )
    assert url_contains_param(
        "is_logged_in",
        "true",
        redirected_url,
    )
    all_nonces = (await db_session.execute(select(Nonce))).scalars().all()
    assert len(all_nonces) == 0

    all_users = (await db_session.execute(select(User))).scalars().all()
    assert len(all_users) == 1
    user = all_users[0]

    assert user.fc_hash == "4abd71ec1f581dce2ea2221cbeac7c973c6aea7bcb835acdfe7d6494f1528060"
    assert user.last_logged_in is not None

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


async def test_login_callback_bad_id_token(
    test_client: TestClient[Litestar],
    db_session: AsyncSession,
    httpx_mock: HTTPXMock,
    decoded_id_token: dict[str, Any],
) -> None:
    NONCE = decoded_id_token["nonce"]
    nonce = Nonce(nonce=NONCE)
    db_session.add(nonce)
    await db_session.commit()

    fake_token_json_response = {
        "access_token": "fake access token",
        "expires_in": 60,
        "scope": "openid given_name family_name preferred_username birthdate gender birthplace birthcountry email",
        "token_type": "Bearer",
    }
    httpx_mock.add_response(
        method="POST",
        url="https://fcp-low.sbx.dev-franceconnect.fr/api/v2/token",
        json=fake_token_json_response,
    )

    response = test_client.get(
        f"/login-callback?code=fake-code&state={nonce.id}", follow_redirects=False
    )

    assert response.status_code == 302
    redirected_url = response.headers["location"]
    assert url_contains_param("error_type", "FranceConnect", redirected_url)
    assert url_contains_param(
        "error", "Erreur lors de la FranceConnexion, veuillez réessayer plus tard.", redirected_url
    )
    assert url_contains_param("code", "missing_id_token", redirected_url)


async def test_login_callback_bad_nonce(
    test_client: TestClient[Litestar],
    db_session: AsyncSession,
    httpx_mock: HTTPXMock,
    monkeypatch: pytest.MonkeyPatch,
    decoded_id_token: dict[str, Any],
) -> None:
    def fake_jwt_decode(*args: Any, **params: Any):
        return decoded_id_token

    monkeypatch.setattr("jwt.decode", fake_jwt_decode)

    NONCE = "some random nonce"
    nonce = Nonce(nonce=NONCE)
    db_session.add(nonce)
    await db_session.commit()

    fake_token_json_response = {
        "access_token": "fake access token",
        "expires_in": 60,
        "id_token": "fake id token",
        "scope": "openid given_name family_name preferred_username birthdate gender birthplace birthcountry email",
        "token_type": "Bearer",
    }
    httpx_mock.add_response(
        method="POST",
        url="https://fcp-low.sbx.dev-franceconnect.fr/api/v2/token",
        json=fake_token_json_response,
        is_reusable=True,
    )
    monkeypatch.setattr("app.controllers.auth.env.FC_AMI_CLIENT_SECRET", "fake-client-secret")

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

    nonce = Nonce(nonce=NONCE)
    db_session.add(nonce)
    await db_session.commit()
    decoded_id_token.pop("nonce")

    response = test_client.get(
        f"/login-callback?code=fake-code&state={nonce.id}", follow_redirects=False
    )

    assert response.status_code == 302
    redirected_url = response.headers["location"]
    assert url_contains_param("error_type", "FranceConnect", redirected_url)
    assert url_contains_param(
        "error", "Erreur lors de la FranceConnexion, veuillez réessayer plus tard.", redirected_url
    )
    assert url_contains_param("code", "missing_nonce", redirected_url)
    all_nonces = (await db_session.execute(select(Nonce))).scalars().all()
    assert len(all_nonces) == 0


async def test_login_callback_bad_token_info(
    test_client: TestClient[Litestar],
    db_session: AsyncSession,
    httpx_mock: HTTPXMock,
    monkeypatch: pytest.MonkeyPatch,
    decoded_id_token: dict[str, Any],
) -> None:
    def fake_jwt_decode(*args: Any, **params: Any):
        return decoded_id_token

    monkeypatch.setattr("jwt.decode", fake_jwt_decode)
    monkeypatch.setattr("app.controllers.auth.env.FC_AMI_CLIENT_SECRET", "fake-client-secret")

    NONCE = decoded_id_token["nonce"]
    nonce = Nonce(nonce=NONCE)
    db_session.add(nonce)
    await db_session.commit()

    fake_token_json_response = {
        "access_token": "fake access token",
        "expires_in": 60,
        "id_token": "fake id token",
        "scope": "openid given_name family_name preferred_username birthdate gender birthplace birthcountry email",
    }
    httpx_mock.add_response(
        method="POST",
        url="https://fcp-low.sbx.dev-franceconnect.fr/api/v2/token",
        json=fake_token_json_response,
    )

    response = test_client.get(
        f"/login-callback?code=fake-code&state={nonce.id}", follow_redirects=False
    )
    redirected_url = response.headers["location"]
    assert url_contains_param("error_type", "FranceConnect", redirected_url)
    assert url_contains_param(
        "error", "Erreur lors de la FranceConnexion, veuillez réessayer plus tard.", redirected_url
    )
    assert url_contains_param("code", "missing_token_type", redirected_url)
    all_nonces = (await db_session.execute(select(Nonce))).scalars().all()
    assert len(all_nonces) == 0

    nonce = Nonce(nonce=NONCE)
    db_session.add(nonce)
    await db_session.commit()

    fake_token_json_response = {
        "expires_in": 60,
        "id_token": "fake id token",
        "scope": "openid given_name family_name preferred_username birthdate gender birthplace birthcountry email",
        "token_type": "Bearer",
    }
    httpx_mock.add_response(
        method="POST",
        url="https://fcp-low.sbx.dev-franceconnect.fr/api/v2/token",
        json=fake_token_json_response,
    )

    response = test_client.get(
        f"/login-callback?code=fake-code&state={nonce.id}", follow_redirects=False
    )
    redirected_url = response.headers["location"]
    assert url_contains_param("error_type", "FranceConnect", redirected_url)
    assert url_contains_param(
        "error", "Erreur lors de la FranceConnexion, veuillez réessayer plus tard.", redirected_url
    )
    assert url_contains_param("code", "missing_access_token", redirected_url)
    all_nonces = (await db_session.execute(select(Nonce))).scalars().all()
    assert len(all_nonces) == 0
