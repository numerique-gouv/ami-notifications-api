import datetime
import json
import uuid
from typing import Any

import pytest
from litestar import Litestar
from litestar.exceptions import WebSocketDisconnect
from litestar.status_codes import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_204_NO_CONTENT,
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
)
from litestar.testing import TestClient
from pytest_httpx import HTTPXMock
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

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

    register_data = {
        "email": "foo@bar.baz",
        "subscription": webpushsubscription,
        "user_id": str(uuid.uuid4()),
    }
    response = test_client.post("/api/v1/registrations", json=register_data)
    assert response.status_code == HTTP_404_NOT_FOUND

    all_registrations = await db_session.execute(select(Registration))
    assert len(all_registrations.scalars().all()) == 0


async def test_register(
    test_client: TestClient[Litestar],
    db_session: AsyncSession,
    webpushsubscription: dict[str, Any],
) -> None:
    user = User(email="alice@example.com")
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    all_registrations = await db_session.execute(select(Registration))
    assert len(all_registrations.scalars().all()) == 0

    # First registration, we're expecting a 201 CREATED.
    register_data = {
        "email": "foo@bar.baz",
        "subscription": webpushsubscription,
        "user_id": str(user.id),
    }
    response = test_client.post("/api/v1/registrations", json=register_data)
    assert response.status_code == HTTP_201_CREATED

    all_registrations = (await db_session.execute(select(Registration))).scalars().all()
    assert len(all_registrations) == 1
    registration = all_registrations[0]
    registration_id = registration.id

    # Second registration, we're expecting a 200 OK, not 201 CREATED.
    register_data = {
        "email": "foo@bar.baz",
        "subscription": webpushsubscription,
        "user_id": str(user.id),
    }
    response = test_client.post("/api/v1/registrations", json=register_data)
    assert response.status_code == HTTP_200_OK

    all_registrations = (await db_session.execute(select(Registration))).scalars().all()
    assert len(all_registrations) == 1
    registration = all_registrations[0]
    assert registration.id == registration_id


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
            "message": "Input should be a valid UUID, invalid length: expected length 32 for simple format, found 0",
            "key": "user_id",
        }
    ]

    # id, created_at and updated_at are ignored
    registration_date: datetime.datetime = datetime.datetime.now(
        datetime.timezone.utc
    ) + datetime.timedelta(days=1)
    registration_id: uuid.UUID = uuid.uuid4()
    registration_data = {
        "email": "foo@bar.baz",
        "subscription": webpushsubscription,
        "user_id": str(user.id),
        "id": str(registration_id),
        "created_at": registration_date.isoformat(),
        "updated_at": registration_date.isoformat(),
    }
    response = test_client.post("/api/v1/registrations", json=registration_data)
    assert response.status_code == HTTP_201_CREATED

    all_registrations = (await db_session.execute(select(Registration))).scalars().all()
    assert len(all_registrations) == 1
    registration = all_registrations[0]
    assert registration.id != registration_id
    assert registration.created_at < registration_date
    assert registration.updated_at < registration_date


async def test_unregister(
    test_client: TestClient[Litestar],
    db_session: AsyncSession,
    registration: Registration,
) -> None:
    all_registrations = (await db_session.execute(select(Registration))).scalars().all()
    assert len(all_registrations) == 1

    response = test_client.delete(f"/api/v1/registrations/{registration.id}")
    assert response.status_code == HTTP_204_NO_CONTENT

    all_registrations = (await db_session.execute(select(Registration))).scalars().all()
    assert len(all_registrations) == 0


async def test_notify_user_does_not_exist(
    test_client: TestClient[Litestar],
) -> None:
    notification_data = {
        "user_id": str(uuid.uuid4()),
        "message": "Hello notification 2",
        "title": "Some notification title",
        "sender": "Jane Doe",
    }
    response = test_client.post("/api/v1/notifications", json=notification_data)
    assert response.status_code == HTTP_404_NOT_FOUND


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
        "user_id": str(registration.user.id),
        "message": "Hello notification 2",
        "title": "Some notification title",
        "sender": "Jane Doe",
    }
    response = test_client.post("/api/v1/notifications", json=notification_data)
    assert response.status_code == HTTP_201_CREATED
    response = test_client.get(f"/api/v1/users/{registration.user.id}/notifications")
    all_notifications = (await db_session.execute(select(Notification))).scalars().all()
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
        "created_at",
    }
    assert response.json()[0]["id"] == str(notification2.id)
    assert response.json()[0]["user_id"] == str(registration.user.id)
    assert response.json()[0]["message"] == "Hello notification 2"
    assert response.json()[0]["title"] == "Some notification title"
    assert response.json()[0]["sender"] == "Jane Doe"
    assert response.json()[0]["unread"] is True
    assert response.json()[0]["created_at"] == notification2.created_at.isoformat().replace(
        "+00:00", "Z"
    )
    assert response.json()[1]["id"] == str(notification.id)
    assert response.json()[1]["user_id"] == str(registration.user.id)
    assert response.json()[1]["message"] == notification.message
    assert response.json()[1]["title"] == notification.title
    assert response.json()[1]["sender"] == notification.sender
    assert response.json()[1]["unread"] is True
    assert response.json()[1]["created_at"] == notification.created_at.isoformat().replace(
        "+00:00", "Z"
    )


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
            "message": "Input should be a valid UUID, invalid length: expected length 32 for simple format, found 0",
            "key": "user_id",
        }
    ]

    # message is required
    notification_data = {
        "user_id": str(user.id),
        "message": "",
        "title": "Some notification title",
        "sender": "Jane Doe",
    }
    response = test_client.post("/api/v1/notifications", json=notification_data)
    assert response.status_code == HTTP_400_BAD_REQUEST
    assert response.json()["extra"] == [
        {"message": "String should have at least 1 character", "key": "message"}
    ]

    # id, created_at, updated_at and unread are ignored
    notification_date: datetime.datetime = datetime.datetime.now(
        datetime.timezone.utc
    ) + datetime.timedelta(days=1)
    notification_id: uuid.UUID = uuid.uuid4()
    notification_data = {
        "user_id": str(user.id),
        "message": "Hello !",
        "title": "Some notification title",
        "sender": "Jane Doe",
        "id": str(notification_id),
        "created_at": notification_date.isoformat(),
        "updated_at": notification_date.isoformat(),
        "unread": False,
    }
    response = test_client.post("/api/v1/notifications", json=notification_data)
    assert response.status_code == HTTP_201_CREATED

    all_notifications = (await db_session.execute(select(Notification))).scalars().all()
    assert len(all_notifications) == 1
    notification = all_notifications[0]
    assert notification.id != notification_id
    assert notification.created_at < notification_date
    assert notification.updated_at < notification_date
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
        "user_id": str(registration.user.id),
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
    assert response.json()[0]["user_id"] == str(notification.user.id)
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
    assert response.json()[0]["user_id"] == str(notification.user.id)
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
    other_notification = Notification(
        user_id=str(other_user.id),
        message="Other notification",
        title="Notification title",
        sender="John Doe",
    )
    db_session.add(other_notification)
    await db_session.commit()

    # invalid, no payload
    response = test_client.patch(f"/api/v1/users/{uuid.uuid4()}/notification/{uuid.uuid4()}/read")
    assert response.status_code == HTTP_400_BAD_REQUEST

    # unknown user
    response = test_client.patch(
        f"/api/v1/users/{uuid.uuid4()}/notification/{uuid.uuid4()}/read", json={"read": True}
    )
    assert response.status_code == HTTP_404_NOT_FOUND

    # can not patch notification of another user
    response = test_client.patch(
        f"/api/v1/users/{notification.user.id}/notification/{other_notification.id}/read",
        json={"read": True},
    )
    assert response.status_code == HTTP_404_NOT_FOUND

    # invalid, read is required
    response = test_client.patch(
        f"/api/v1/users/{notification.user.id}/notification/{notification.id}/read",
        json={"read": None},
    )
    assert response.status_code == HTTP_400_BAD_REQUEST
    assert response.json()["extra"] == [
        {"message": "Input should be a valid boolean", "key": "read"}
    ]

    response = test_client.patch(
        f"/api/v1/users/{notification.user.id}/notification/{notification.id}/read",
        json={"read": True},
    )
    assert response.status_code == HTTP_200_OK
    assert response.json()["user_id"] == str(notification.user.id)
    assert response.json()["message"] == notification.message
    assert response.json()["title"] == notification.title
    assert response.json()["sender"] == notification.sender
    assert response.json()["unread"] is False

    response = test_client.patch(
        f"/api/v1/users/{notification.user.id}/notification/{notification.id}/read",
        json={"read": False},
    )
    assert response.status_code == HTTP_200_OK
    assert response.json()["user_id"] == str(notification.user.id)
    assert response.json()["message"] == notification.message
    assert response.json()["title"] == notification.title
    assert response.json()["sender"] == notification.sender
    assert response.json()["unread"] is True


async def test_stream_notification_events_user_does_not_exist(
    test_client: TestClient[Litestar],
) -> None:
    with pytest.raises(WebSocketDisconnect):
        with test_client.websocket_connect(
            f"/api/v1/users/{uuid.uuid4()}/notification/events/stream"
        ):
            # When the user doesn't exist socket is immediately closed
            pass


async def test_stream_notification_events_created(
    test_client: TestClient[Litestar],
    db_session: AsyncSession,
    user: User,
) -> None:
    all_notifications = (await db_session.execute(select(Notification))).scalars().all()
    assert len(all_notifications) == 0

    with test_client.websocket_connect(f"/api/v1/users/{user.id}/notification/events/stream") as ws:
        try:
            # create a notification
            notification_data = {
                "user_id": str(user.id),
                "message": "Hello notification",
                "title": "Some notification title",
                "sender": "Jane Doe",
            }
            response = test_client.post("/api/v1/notifications", json=notification_data)
            assert response.status_code == HTTP_201_CREATED
            all_notifications = (await db_session.execute(select(Notification))).scalars().all()
            assert len(all_notifications) == 1
            notification = all_notifications[0]

            # notification event is streamed
            message = ws.receive_json()
            assert message == {
                "id": str(notification.id),
                "user_id": str(user.id),
                "event": "created",
            }
        finally:
            ws.send_text("close")


async def test_stream_notification_events_updated(
    test_client: TestClient[Litestar],
    db_session: AsyncSession,
    user: User,
    notification: Notification,
) -> None:
    all_notifications = (await db_session.execute(select(Notification))).scalars().all()
    assert len(all_notifications) == 1

    with test_client.websocket_connect(f"/api/v1/users/{user.id}/notification/events/stream") as ws:
        try:
            # create a notification for another user
            other_user = User(
                email="other-user@example.com", family_name="AMI", given_name="Other Test User"
            )
            db_session.add(other_user)
            await db_session.commit()
            notification_data = {
                "user_id": str(other_user.id),
                "message": "Hello other notification",
                "title": "Some notification title",
                "sender": "Jane Doe",
            }
            response = test_client.post("/api/v1/notifications", json=notification_data)
            assert response.status_code == HTTP_201_CREATED

            # mark user notification as read
            response = test_client.patch(
                f"/api/v1/users/{notification.user.id}/notification/{notification.id}/read",
                json={"read": True},
            )
            assert response.status_code == HTTP_200_OK

            # only read notification event is streamed: other user notification had no effect for this socket
            message = ws.receive_json()
            assert message == {
                "id": str(notification.id),
                "user_id": str(user.id),
                "event": "updated",
            }
        finally:
            ws.send_text("close")


async def test_list_registrations_user_does_not_exist(
    test_client: TestClient[Litestar],
) -> None:
    response = test_client.get("/api/v1/users/0/registrations")
    assert response.status_code == HTTP_404_NOT_FOUND


async def test_list_registrations(
    test_client: TestClient[Litestar],
    registration: Registration,
) -> None:
    response = test_client.get(f"/api/v1/users/{registration.user.id}/registrations")
    assert response.status_code == HTTP_200_OK
    registrations = response.json()
    assert len(registrations) == 1
    assert set(response.json()[0].keys()) == {"id", "user_id", "subscription", "created_at"}
    assert response.json()[0]["id"] == str(registration.id)
    assert response.json()[0]["user_id"] == str(registration.user_id)
    assert response.json()[0]["subscription"] == registration.subscription
    assert response.json()[0]["created_at"] == registration.created_at.isoformat().replace(
        "+00:00", "Z"
    )


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

    assert user.email == "angela@dubois.fr"
    assert user.given_name == "Angela Claire Louise"
    assert user.family_name == "DUBOIS"
    assert user.birthdate == datetime.date(1962, 8, 24)
    assert user.gender == "female"
    assert user.birthplace == 75107
    assert user.birthcountry == 99100

    response = test_client.get("/fc_userinfo", headers=auth)

    assert response.status_code == 200
    assert json.loads(response.text) == {
        "user_id": str(user.id),
        "user_data": fake_userinfo_token,
    }


async def test_get_sector_identifier_url(
    test_client: TestClient[Litestar],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "app.env.PUBLIC_SECTOR_IDENTIFIER_URL", "  https://example.com  \nfoobar \n"
    )
    response = test_client.get("/sector_identifier_url")
    assert response.json() == ["https://example.com", "foobar"]
