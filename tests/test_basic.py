import datetime
import json
from typing import Any
from urllib.parse import urlencode

import pytest
from litestar import Litestar
from litestar.status_codes import HTTP_200_OK, HTTP_201_CREATED, HTTP_404_NOT_FOUND
from litestar.testing import TestClient
from pytest_httpx import HTTPXMock
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.database import DonneesPivot, Notification, Registration, User

FAKE_USERINFO = {
    "sub": "fake sub",
    "given_name": "Angela Claire Louise",
    "given_name_array": ["Angela", "Claire", "Louise"],
    "family_name": "DUBOIS",
    "birthdate": "1962-08-24",
    "birthcountry": "99100",
    "birthplace": "75107",
    "gender": "female",
    "email": "angela@dubois.fr",
    "aud": "fake aud",
    "exp": 1753877658,
    "iat": 1753877598,
    "iss": "https://fcp-low.sbx.dev-franceconnect.fr/api/v2",
}


async def test_notifications_empty(
    test_client: TestClient[Litestar], user: User
) -> None:  # The `user` fixture is needed so we don't get a 404 when asking for notifications.
    response = test_client.get(f"/api/v1/users/{user.id}/notifications")
    assert response.status_code == HTTP_200_OK
    assert response.json() == []


async def test_notifications(test_client: TestClient[Litestar], notification: Notification) -> None:
    response = test_client.get(f"/api/v1/users/{notification.user.id}/notifications")
    assert response.status_code == HTTP_200_OK
    assert len(response.json()) == 1
    assert response.json()[0]["user_id"] == notification.user.id
    assert response.json()[0]["message"] == notification.message
    assert response.json()[0]["title"] == notification.title
    assert response.json()[0]["sender"] == notification.sender


async def test_create_notification_from_test_and_from_app_context(
    test_client: TestClient[Litestar],
    notification: Notification,
    registration: Registration,
    httpx_mock: HTTPXMock,
) -> None:
    """This test makes sure we're using the same database session in tests and through the API.

    Validate that we can create entries in the database from the test itself (using a fixture)
    and from the API, and both are using the same database session.
    """
    # Make sure we don't even try sending a notification to a push server.
    httpx_mock.add_response(url=registration.subscription["endpoint"])
    notification_data = {
        "user_id": registration.user.id,
        "message": "Hello notification 2",
        "title": "Some notification title",
        "sender": "Jane Doe",
    }
    response = test_client.post("/api/v1/notifications", json=notification_data)
    assert response.status_code == HTTP_201_CREATED
    response = test_client.get(f"/api/v1/users/{registration.user.id}/notifications")
    assert response.status_code == HTTP_200_OK
    assert len(response.json()) == 2
    assert response.json()[0]["user_id"] == registration.user.id
    assert response.json()[0]["message"] == notification.message
    assert response.json()[0]["title"] == notification.title
    assert response.json()[0]["sender"] == notification.sender
    assert response.json()[1]["user_id"] == registration.user.id
    assert response.json()[1]["message"] == "Hello notification 2"
    assert response.json()[1]["title"] == "Some notification title"
    assert response.json()[1]["sender"] == "Jane Doe"


async def test_register_user_does_not_exist(
    test_client: TestClient[Litestar],
    db_session: AsyncSession,
    webpushsubscription: dict[str, Any],
) -> None:
    user = User(email="alice@example.com")
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    fake_id: int = 0
    register_data = {
        "email": "foo@bar.baz",
        "subscription": webpushsubscription,
        "user_id": fake_id,
    }
    response = test_client.post("/api/v1/registrations", json=register_data)
    assert response.status_code == HTTP_404_NOT_FOUND

    all_registrations = await db_session.exec(select(Registration))
    assert len(all_registrations.all()) == 0


async def test_register(
    test_client: TestClient[Litestar],
    db_session: AsyncSession,
    webpushsubscription: dict[str, Any],
) -> None:
    user = User(email="alice@example.com")
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    all_registrations = await db_session.exec(select(Registration))
    assert len(all_registrations.all()) == 0

    # First registration, we're expecting a 201 CREATED.
    register_data = {
        "email": "foo@bar.baz",
        "subscription": webpushsubscription,
        "user_id": user.id,
    }
    response = test_client.post("/api/v1/registrations", json=register_data)
    assert response.status_code == HTTP_201_CREATED

    all_registrations = (await db_session.exec(select(Registration))).all()
    assert len(all_registrations) == 1
    registration = all_registrations[0]
    assert registration.id == 1

    # Second registration, we're expecting a 200 OK, not 201 CREATED.
    register_data = {
        "email": "foo@bar.baz",
        "subscription": webpushsubscription,
        "user_id": user.id,
    }
    response = test_client.post("/api/v1/registrations", json=register_data)
    assert response.status_code == HTTP_200_OK

    all_registrations = (await db_session.exec(select(Registration))).all()
    assert len(all_registrations) == 1
    registration = all_registrations[0]
    assert registration.id == 1


async def test_list_users(
    test_client: TestClient[Litestar],
    user: User,
) -> None:
    response = test_client.get("/api/v1/users")
    assert response.status_code == HTTP_200_OK
    users = response.json()
    assert len(users) == 1
    assert users[0]["email"] == user.email


async def test_list_registrations(
    test_client: TestClient[Litestar],
    registration: Registration,
) -> None:
    response = test_client.get(f"/api/v1/users/{registration.user.id}/registrations")
    assert response.status_code == HTTP_200_OK
    registrations = response.json()
    assert len(registrations) == 1


async def test_ami_login_callback(
    test_client: TestClient[Litestar],
    httpx_mock: HTTPXMock,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
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
    monkeypatch.setattr("app.FC_AMI_CLIENT_SECRET", "fake-client-secret")

    response = test_client.get("/login-callback?code=fake-code", follow_redirects=False)

    assert response.status_code == 302
    redirected_url = response.headers["location"]
    assert redirected_url.startswith("https://localhost:5173")
    assert "access_token" in redirected_url
    assert "scope" in redirected_url
    assert "id_token" in redirected_url
    assert "token_type" in redirected_url
    assert "is_logged_in" in redirected_url


async def test_ami_fc_get_userinfo(
    test_client: TestClient[Litestar],
    db_session: AsyncSession,
    httpx_mock: HTTPXMock,
    monkeypatch: pytest.MonkeyPatch,
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
        return FAKE_USERINFO

    monkeypatch.setattr("jwt.decode", fake_jwt_decode)

    response = test_client.get("/fc_userinfo", headers=auth)

    assert response.status_code == 200
    assert json.loads(response.text) == {
        "user_id": 1,
        "user_data": fake_userinfo_token,
    }

    all_users = (await db_session.exec(select(User, DonneesPivot).join(DonneesPivot))).all()
    assert len(all_users) == 1
    user, donnees_pivot = all_users[0]
    assert user.id == 1
    assert user.email == "angela@dubois.fr"
    assert donnees_pivot.id == 1
    assert donnees_pivot.user_id == 1
    assert donnees_pivot.given_name == "Angela Claire Louise"
    assert donnees_pivot.family_name == "DUBOIS"
    assert donnees_pivot.birthdate == datetime.datetime(1962, 8, 24, 0, 0)
    assert donnees_pivot.gender == "female"
    assert donnees_pivot.birthplace == 75107
    assert donnees_pivot.birthcountry == 99100

    response = test_client.get("/fc_userinfo", headers=auth)

    assert response.status_code == 200
    assert json.loads(response.text) == {
        "user_id": 1,
        "user_data": fake_userinfo_token,
    }
    all_users = (await db_session.exec(select(User, DonneesPivot).join(DonneesPivot))).all()
    assert len(all_users) == 1
    user, donnees_pivot = all_users[0]
    assert user.id == 1
    assert donnees_pivot.id == 1
    assert donnees_pivot.user_id == 1


async def test_rvo_login_callback(
    test_client: TestClient[Litestar],
    httpx_mock: HTTPXMock,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
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
    httpx_mock.add_response(
        method="GET", url="https://fcp-low.sbx.dev-franceconnect.fr/api/v2/jwks"
    )
    httpx_mock.add_response(
        method="GET",
        url="https://fcp-low.sbx.dev-franceconnect.fr/api/v2/userinfo",
        json=FAKE_USERINFO,
    )

    def fake_jwt_decode(*args: Any, **params: Any):
        return FAKE_USERINFO

    monkeypatch.setattr("jwt.decode", fake_jwt_decode)

    response = test_client.get("/rvo/login-callback?code=fake-code")

    assert response.request.url == "http://testserver.local/rvo"
    assert test_client.get_session_data() == {
        "id_token": "fake id token",
        "userinfo": FAKE_USERINFO,
    }


async def test_rvo_logout(
    test_client: TestClient[Litestar],
) -> None:
    test_client.set_session_data({"id_token": "fake id token", "userinfo": FAKE_USERINFO})
    data: dict[str, str] = {
        "id_token_hint": "fake id token",
        "state": "not-implemented-yet-and-has-more-than-32-chars",
        "post_logout_redirect_uri": "https://localhost:8000/rvo/logout-callback",
    }
    params: str = urlencode(data)
    url: str = f"https://fcp-low.sbx.dev-franceconnect.fr/api/v2/session/end?{params}"

    response = test_client.get("/rvo/logout", follow_redirects=False)
    assert response.status_code == 302
    assert response.headers["location"] == url
    # Session data is still present, so if logging out from FC failed, the user can try again.
    assert test_client.get_session_data() == {
        "id_token": "fake id token",
        "userinfo": FAKE_USERINFO,
    }


async def test_rvo_logout_callback(
    test_client: TestClient[Litestar],
) -> None:
    test_client.set_session_data({"id_token": "fake id token", "userinfo": FAKE_USERINFO})
    response = test_client.get("/rvo/logout-callback", follow_redirects=False)
    assert response.status_code == 302
    # As the user was properly logged out from FC, the local session is now emptied, and the user redirected to the fake service provider.
    assert response.headers["location"] == "/rvo/logged_out"
    assert test_client.get_session_data() == {}


async def test_rvo_home_when_logged_in(
    test_client: TestClient[Litestar],
) -> None:
    test_client.set_session_data({"id_token": "fake id token", "userinfo": FAKE_USERINFO})
    response = test_client.get("/rvo", follow_redirects=False)
    assert response.status_code == 200
    assert "/rvo/detail/1" in response.text
    assert "/rvo/detail/2" in response.text


async def test_rvo_detail_when_logged_in(
    test_client: TestClient[Litestar],
) -> None:
    test_client.set_session_data({"id_token": "fake id token", "userinfo": FAKE_USERINFO})
    response = test_client.get("/rvo/detail/1", follow_redirects=False)
    assert "Rendez-vous dans votre Agence France Travail Paris 18e Ney" in response.text
    assert response.status_code == 200
    assert "Annuler le RDV" in response.text

    response = test_client.get("/rvo/detail/2", follow_redirects=False)
    assert "Rendez-vous dans votre Maison France Services" in response.text
    assert response.status_code == 200
    assert "Annuler le RDV" in response.text


async def test_rvo_detail_when_logged_out(
    test_client: TestClient[Litestar],
) -> None:
    detail_url = "/rvo/detail/1"
    response = test_client.get(detail_url, follow_redirects=False)
    assert response.status_code == 302
    assert "redirect_once_connected" in test_client.get_session_data()
    assert (
        test_client.get_session_data()["redirect_once_connected"]
        == f"http://testserver.local{detail_url}"
    )


async def test_get_sector_identifier_url(
    test_client: TestClient[Litestar],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr("app.PUBLIC_SECTOR_IDENTIFIER_URL", "  https://example.com  \nfoobar \n")
    response = test_client.get("/sector_identifier_url")
    assert response.json() == ["https://example.com", "foobar"]
