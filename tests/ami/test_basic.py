import datetime
import json
from typing import Any

import pytest
from litestar import Litestar
from litestar.status_codes import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
)
from litestar.testing import TestClient
from pytest_httpx import HTTPXMock
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models import Notification, Registration, User


async def test_register_user_does_not_exist(
    test_client: TestClient[Litestar],
    db_session: AsyncSession,
    webpushsubscription: dict[str, Any],
) -> None:
    user = User(email="alice@example.com")
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    fake_id: str = "0"
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
        "user_id": str(user.id),
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
        "user_id": str(user.id),
    }
    response = test_client.post("/api/v1/registrations", json=register_data)
    assert response.status_code == HTTP_200_OK

    all_registrations = (await db_session.exec(select(Registration))).all()
    assert len(all_registrations) == 1
    registration = all_registrations[0]
    assert registration.id == 1


async def test_register_fields(
    test_client: TestClient[Litestar],
    db_session: AsyncSession,
    webpushsubscription: dict[str, Any],
) -> None:
    user = User(email="alice@example.com")
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    # user_id is required
    register_data = {
        "email": "foo@bar.baz",
        "subscription": webpushsubscription,
        "user_id": "",
    }
    response = test_client.post("/api/v1/registrations", json=register_data)
    assert response.status_code == HTTP_400_BAD_REQUEST
    assert response.json()["extra"] == [
        {
            "message": "Input should be a valid integer, unable to parse string as an integer",
            "key": "user_id",
        }
    ]

    # id and created_at are ignored
    registration_date: datetime.datetime = datetime.datetime.now() + datetime.timedelta(days=1)
    registration_data = {
        "email": "foo@bar.baz",
        "subscription": webpushsubscription,
        "user_id": str(user.id),
        "id": 0,
        "created_at": registration_date.isoformat(),
    }
    response = test_client.post("/api/v1/registrations", json=registration_data)
    assert response.status_code == HTTP_201_CREATED

    all_registrations = (await db_session.exec(select(Registration))).all()
    assert len(all_registrations) == 1
    registration = all_registrations[0]
    assert registration.id
    assert registration.id > 0
    assert registration.created_at < registration_date


async def test_notify_create_notification_from_test_and_from_app_context(
    test_client: TestClient[Litestar],
    db_session: AsyncSession,
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
    all_notifications = (await db_session.exec(select(Notification))).all()
    assert len(all_notifications) == 2
    notification2 = all_notifications[1]
    assert response.status_code == HTTP_200_OK
    assert len(response.json()) == 2
    assert set(response.json()[0].keys()) == {
        "id",
        "user_id",
        "message",
        "title",
        "sender",
        "unread",
        "date",
    }
    assert response.json()[0]["id"] == notification2.id
    assert response.json()[0]["user_id"] == registration.user.id
    assert response.json()[0]["message"] == "Hello notification 2"
    assert response.json()[0]["title"] == "Some notification title"
    assert response.json()[0]["sender"] == "Jane Doe"
    assert response.json()[0]["unread"] is True
    assert response.json()[0]["date"] == notification2.date.isoformat()
    assert response.json()[1]["id"] == notification.id
    assert response.json()[1]["user_id"] == registration.user.id
    assert response.json()[1]["message"] == notification.message
    assert response.json()[1]["title"] == notification.title
    assert response.json()[1]["sender"] == notification.sender
    assert response.json()[1]["unread"] is True
    assert response.json()[1]["date"] == notification.date.isoformat()


async def test_notify_create_notification_test_fields(
    test_client: TestClient[Litestar],
    db_session: AsyncSession,
    user: User,
) -> None:
    # user_id is required
    notification_data = {
        "user_id": "",
        "message": "Hello !",
        "title": "Some notification title",
        "sender": "Jane Doe",
    }
    response = test_client.post("/api/v1/notifications", json=notification_data)
    assert response.status_code == HTTP_400_BAD_REQUEST
    assert response.json()["extra"] == [
        {
            "message": "Input should be a valid integer, unable to parse string as an integer",
            "key": "user_id",
        }
    ]

    # message is required
    notification_data = {
        "user_id": user.id,
        "message": "",
        "title": "Some notification title",
        "sender": "Jane Doe",
    }
    response = test_client.post("/api/v1/notifications", json=notification_data)
    assert response.status_code == HTTP_400_BAD_REQUEST
    assert response.json()["extra"] == [
        {"message": "String should have at least 1 character", "key": "message"}
    ]

    # id, date and unread are ignored
    notification_date: datetime.datetime = datetime.datetime.now() + datetime.timedelta(days=1)
    notification_data = {
        "user_id": user.id,
        "message": "Hello !",
        "title": "Some notification title",
        "sender": "Jane Doe",
        "id": 0,
        "date": notification_date.isoformat(),
        "unread": False,
    }
    response = test_client.post("/api/v1/notifications", json=notification_data)
    assert response.status_code == HTTP_201_CREATED

    all_notifications = (await db_session.exec(select(Notification))).all()
    assert len(all_notifications) == 1
    notification = all_notifications[0]
    assert notification.id
    assert notification.id > 0
    assert notification.date < notification_date
    assert notification.unread is True


async def test_notify_when_registration_gone(
    test_client: TestClient[Litestar],
    registration: Registration,
    httpx_mock: HTTPXMock,
) -> None:
    """When somebody revokes a PUSH authorization (a push registration), then trying to
    push on this registration will be answered with a status 410 GONE.

    This shouldn't fail the notification process.
    """
    # Make sure we don't even try sending a notification to a push server.
    httpx_mock.add_response(url=registration.subscription["endpoint"], status_code=410)
    notification_data = {
        "user_id": registration.user.id,
        "message": "This will not be PUSHed, but still created on the backend",
        "title": "Some notification title",
        "sender": "Jane Doe",
    }
    response = test_client.post("/api/v1/notifications", json=notification_data)
    assert response.status_code == HTTP_201_CREATED
    response = test_client.get(f"/api/v1/users/{registration.user.id}/notifications")
    assert response.status_code == HTTP_200_OK
    assert len(response.json()) == 1


async def test_get_notifications_should_return_empty_list_by_default(
    test_client: TestClient[Litestar], user: User
) -> None:  # The `user` fixture is needed so we don't get a 404 when asking for notifications.
    response = test_client.get(f"/api/v1/users/{user.id}/notifications")
    assert response.status_code == HTTP_200_OK
    assert response.json() == []


async def test_get_notifications_should_return_notifications_for_given_user_id(
    test_client: TestClient[Litestar],
    db_session: AsyncSession,
    notification: Notification,
) -> None:
    # notification for another user, not returned in notification list of test user
    other_user = User(
        email="other-user@example.com", family_name="AMI", given_name="Other Test User"
    )
    db_session.add(other_user)
    await db_session.commit()
    assert other_user.id is not None, "User ID should be set"
    other_notification = Notification(
        user_id=other_user.id,
        message="Other notification",
        title="Notification title",
        sender="John Doe",
    )
    db_session.add(other_notification)
    await db_session.commit()

    # unknown user
    response = test_client.get("/api/v1/users/0/notifications")
    assert response.status_code == HTTP_404_NOT_FOUND

    # test user notification list
    response = test_client.get(f"/api/v1/users/{notification.user.id}/notifications")
    assert response.status_code == HTTP_200_OK
    assert len(response.json()) == 1
    assert response.json()[0]["user_id"] == notification.user.id
    assert response.json()[0]["message"] == notification.message
    assert response.json()[0]["title"] == notification.title
    assert response.json()[0]["sender"] == notification.sender
    assert response.json()[0]["unread"] is True

    response = test_client.get(f"/api/v1/users/{notification.user.id}/notifications?unread=true")
    assert response.status_code == HTTP_200_OK
    assert len(response.json()) == 1
    response = test_client.get(f"/api/v1/users/{notification.user.id}/notifications?unread=false")
    assert response.status_code == HTTP_200_OK
    assert len(response.json()) == 0

    notification.unread = False
    db_session.add(notification)
    await db_session.commit()

    response = test_client.get(f"/api/v1/users/{notification.user.id}/notifications")
    assert response.status_code == HTTP_200_OK
    assert len(response.json()) == 1
    assert response.json()[0]["user_id"] == notification.user.id
    assert response.json()[0]["message"] == notification.message
    assert response.json()[0]["title"] == notification.title
    assert response.json()[0]["sender"] == notification.sender
    assert response.json()[0]["unread"] is False

    response = test_client.get(f"/api/v1/users/{notification.user.id}/notifications?unread=true")
    assert response.status_code == HTTP_200_OK
    assert len(response.json()) == 0
    response = test_client.get(f"/api/v1/users/{notification.user.id}/notifications?unread=false")
    assert response.status_code == HTTP_200_OK
    assert len(response.json()) == 1


async def test_read_notification(
    test_client: TestClient[Litestar],
    db_session: AsyncSession,
    notification: Notification,
) -> None:
    # notification for another user, can not be patched by test user
    other_user = User(
        email="other-user@example.com", family_name="AMI", given_name="Other Test User"
    )
    db_session.add(other_user)
    await db_session.commit()
    assert other_user.id is not None, "User ID should be set"
    other_notification = Notification(
        user_id=other_user.id,
        message="Other notification",
        title="Notification title",
        sender="John Doe",
    )
    db_session.add(other_notification)
    await db_session.commit()

    # invalid, no payload
    response = test_client.patch("/api/v1/users/0/notification/0/read")
    assert response.status_code == HTTP_400_BAD_REQUEST

    # unknown user
    response = test_client.patch("/api/v1/users/0/notification/0/read", json={"read": True})
    assert response.status_code == HTTP_404_NOT_FOUND

    # can not patch notification of another user
    response = test_client.patch(
        f"/api/v1/users/{notification.user.id}/notification/{other_notification.id}/read",
        json={"read": True},
    )
    assert response.status_code == HTTP_404_NOT_FOUND

    response = test_client.patch(
        f"/api/v1/users/{notification.user.id}/notification/{notification.id}/read",
        json={"read": True},
    )
    assert response.status_code == HTTP_200_OK
    assert response.json()["user_id"] == notification.user.id
    assert response.json()["message"] == notification.message
    assert response.json()["title"] == notification.title
    assert response.json()["sender"] == notification.sender
    assert response.json()["unread"] is False

    response = test_client.patch(
        f"/api/v1/users/{notification.user.id}/notification/{notification.id}/read",
        json={"read": False},
    )
    assert response.status_code == HTTP_200_OK
    assert response.json()["user_id"] == notification.user.id
    assert response.json()["message"] == notification.message
    assert response.json()["title"] == notification.title
    assert response.json()["sender"] == notification.sender
    assert response.json()["unread"] is True


async def test_list_registrations(
    test_client: TestClient[Litestar],
    registration: Registration,
) -> None:
    response = test_client.get(f"/api/v1/users/{registration.user.id}/registrations")
    assert response.status_code == HTTP_200_OK
    registrations = response.json()
    assert len(registrations) == 1
    assert set(response.json()[0].keys()) == {"id", "user_id", "subscription", "created_at"}
    assert response.json()[0]["id"] == registration.id
    assert response.json()[0]["user_id"] == registration.user_id
    assert response.json()[0]["subscription"] == registration.subscription
    assert response.json()[0]["created_at"] == registration.created_at.isoformat()


async def test_login_callback(
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
    monkeypatch.setattr("app.env.FC_AMI_CLIENT_SECRET", "fake-client-secret")

    response = test_client.get("/login-callback?code=fake-code", follow_redirects=False)

    assert response.status_code == 302
    redirected_url = response.headers["location"]
    assert redirected_url.startswith("https://localhost:5173")
    assert "access_token" in redirected_url
    assert "scope" in redirected_url
    assert "id_token" in redirected_url
    assert "token_type" in redirected_url
    assert "is_logged_in" in redirected_url


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
    assert json.loads(response.text) == {
        "user_id": 1,
        "user_data": fake_userinfo_token,
    }

    all_users = (await db_session.exec(select(User))).all()
    assert len(all_users) == 1
    user = all_users[0]
    assert user.id == 1
    assert user.email == "angela@dubois.fr"
    assert user.id == 1
    assert user.given_name == "Angela Claire Louise"
    assert user.family_name == "DUBOIS"
    assert user.birthdate == datetime.date(1962, 8, 24)
    assert user.gender == "female"
    assert user.birthplace == 75107
    assert user.birthcountry == 99100

    response = test_client.get("/fc_userinfo", headers=auth)

    assert response.status_code == 200
    assert json.loads(response.text) == {
        "user_id": 1,
        "user_data": fake_userinfo_token,
    }


async def test_get_api_particulier_quotient(
    test_client: TestClient[Litestar],
    httpx_mock: HTTPXMock,
) -> None:
    fake_quotient_data = {"foo": "bar"}
    auth = {"authorization": "Bearer foobar_access_token"}
    httpx_mock.add_response(
        method="GET",
        url="https://staging.particulier.api.gouv.fr/v3/dss/quotient_familial/france_connect?recipient=13002526500013",
        match_headers=auth,
        json=fake_quotient_data,
    )
    response = test_client.get("/api-particulier/quotient", headers=auth)

    assert response.status_code == 200
    assert json.loads(response.text) == fake_quotient_data


async def test_get_sector_identifier_url(
    test_client: TestClient[Litestar],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "app.env.PUBLIC_SECTOR_IDENTIFIER_URL", "  https://example.com  \nfoobar \n"
    )
    response = test_client.get("/sector_identifier_url")
    assert response.json() == ["https://example.com", "foobar"]
