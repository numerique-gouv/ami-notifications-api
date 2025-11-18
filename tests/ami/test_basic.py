import datetime
import json
import uuid
from base64 import urlsafe_b64encode
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

from app import env
from app.auth import generate_nonce
from app.models import Notification, Registration, User
from tests.utils import url_contains_param


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
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    FAKE_NONCE = "some-random-nonce"
    monkeypatch.setattr("app.controllers.auth.generate_nonce", lambda: FAKE_NONCE)
    response = test_client.get("/login-france-connect", follow_redirects=False)
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
    assert url_contains_param("state", env.PUBLIC_FC_AMI_REDIRECT_URL, redirected_url)
    assert url_contains_param("nonce", FAKE_NONCE, redirected_url)
    assert url_contains_param("acr_values", "eidas1", redirected_url)
    assert url_contains_param("prompt", "login", redirected_url)


async def test_login_callback(
    test_client: TestClient[Litestar],
    httpx_mock: HTTPXMock,
    monkeypatch: pytest.MonkeyPatch,
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
    monkeypatch.setattr("app.env.FC_AMI_CLIENT_SECRET", "fake-client-secret")

    test_client.set_session_data({"nonce": NONCE, "state": STATE})
    response = test_client.get(
        f"/login-callback?code=fake-code&state={STATE}", follow_redirects=False
    )

    assert response.status_code == 302
    redirected_url = response.headers["location"]
    assert redirected_url.startswith("https://localhost:5173")
    assert "access_token" in redirected_url
    assert "scope" in redirected_url
    assert "id_token" in redirected_url
    assert "token_type" in redirected_url
    assert "is_logged_in" in redirected_url
    assert "nonce" not in test_client.get_session_data()
    assert "state" not in test_client.get_session_data()


async def test_login_callback_token_query_failure(
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
    response = test_client.get(
        f"/login-callback?code=fake-code&state={STATE}", follow_redirects=False
    )

    assert response.status_code == 302
    redirected_url = response.headers["location"]
    assert (
        redirected_url
        == "https://localhost:5173/?error=Erreur+lors+de+la+France+Connexion%2C+veuillez+r%C3%A9essayer+plus+tard.&error_type=FranceConnect"
    )


async def test_login_callback_bad_nonce(
    test_client: TestClient[Litestar],
    httpx_mock: HTTPXMock,
    monkeypatch: pytest.MonkeyPatch,
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
    monkeypatch.setattr("app.env.FC_AMI_CLIENT_SECRET", "fake-client-secret")

    STATE = "some random state"
    test_client.set_session_data({"nonce": "some other nonce", "state": STATE})
    response = test_client.get(
        f"/login-callback?code=fake-code&state={STATE}", follow_redirects=False
    )

    assert response.status_code == 302
    redirected_url = response.headers["location"]
    assert (
        redirected_url
        == "https://localhost:5173/?error=Erreur+lors+de+la+France+Connexion%2C+veuillez+r%C3%A9essayer+plus+tard.&error_type=FranceConnect"
    )


async def test_login_callback_bad_state(
    test_client: TestClient[Litestar],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr("app.env.FC_AMI_CLIENT_SECRET", "fake-client-secret")

    STATE = "some random state"
    test_client.set_session_data({"nonce": "some other nonce", "state": "some other state"})
    response = test_client.get(
        f"/login-callback?code=fake-code&state={STATE}", follow_redirects=False
    )

    assert response.status_code == 302
    redirected_url = response.headers["location"]
    assert (
        redirected_url
        == "https://localhost:5173/?error=Erreur+lors+de+la+France+Connexion%2C+veuillez+r%C3%A9essayer+plus+tard.&error_type=FranceConnect"
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
    assert (
        redirected_url
        == "https://localhost:5173/?error=access_denied&error_type=FranceConnect&error_description=User+auth+aborted"
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
