import datetime
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
    assert url_contains_param("idp_hint", env.PUBLIC_FC_AMI_IDP_HINT, redirected_url)


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
    monkeypatch.setattr("app.env.FC_AMI_CLIENT_SECRET", "fake-client-secret")

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
    monkeypatch.setattr("app.env.FC_AMI_CLIENT_SECRET", "fake-client-secret")

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
    monkeypatch.setattr("app.env.FC_AMI_CLIENT_SECRET", "fake-client-secret")

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
    monkeypatch.setattr("app.env.FC_AMI_CLIENT_SECRET", "fake-client-secret")

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
        "error_uri": "https://docs.partenaires.franceconnect.gouv.fr/fs/fs-technique/fs-technique-erreurs/"
        "?code=Y049E20B&id=801d508c-72d7-459d-8947-104cf89ce015",
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


async def test_login_callback_userinfo_query_failure(
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
        "token_type": "Bearer",
    }
    httpx_mock.add_response(
        method="POST",
        url="https://fcp-low.sbx.dev-franceconnect.fr/api/v2/token",
        json=fake_token_json_response,
    )

    auth = {"authorization": "Bearer fake access token"}
    httpx_mock.add_response(
        method="GET",
        url="https://fcp-low.sbx.dev-franceconnect.fr/api/v2/userinfo",
        match_headers=auth,
        status_code=500,
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


async def test_login_callback_error(
    test_client: TestClient[Litestar],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_retry():
        raise Exception()

    monkeypatch.setattr("app.controllers.auth.retry_fc_later", fake_retry)
    response = test_client.get("/login-callback?state=some-state", follow_redirects=False)
    redirected_url = response.headers["location"]
    assert redirected_url == "https://localhost:5173/#/technical-error"


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
