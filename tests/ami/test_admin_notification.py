import datetime
import uuid

from litestar import Litestar
from litestar.status_codes import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
)
from litestar.testing import TestClient
from pytest_httpx import HTTPXMock
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Notification, Registration, User
from tests.ami.utils import login


async def test_admin_notify_user_does_not_exist(
    test_client: TestClient[Litestar],
) -> None:
    notification_data = {
        "user_id": str(uuid.uuid4()),
        "message": "Hello notification 2",
        "title": "Some notification title",
        "sender": "Jane Doe",
    }
    response = test_client.post("/ami_admin/notifications", json=notification_data)
    assert response.status_code == HTTP_404_NOT_FOUND


async def test_admin_notify_create_notification_from_test_and_from_app_context(
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
    response = test_client.post("/ami_admin/notifications", json=notification_data)
    assert response.status_code == HTTP_201_CREATED
    login(registration.user, test_client)
    response = test_client.get("/api/v1/users/notifications")
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


async def test_admin_notify_create_notification_test_fields(
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
    response = test_client.post("/ami_admin/notifications", json=notification_data)
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
    response = test_client.post("/ami_admin/notifications", json=notification_data)
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
    response = test_client.post("/ami_admin/notifications", json=notification_data)
    assert response.status_code == HTTP_201_CREATED

    all_notifications = (await db_session.execute(select(Notification))).scalars().all()
    assert len(all_notifications) == 1
    notification = all_notifications[0]
    assert notification.id != notification_id
    assert notification.created_at < notification_date
    assert notification.updated_at < notification_date
    assert notification.unread is True


async def test_admin_notify_when_registration_gone(
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
    response = test_client.post("/ami_admin/notifications", json=notification_data)
    assert response.status_code == HTTP_201_CREATED
    login(registration.user, test_client)
    response = test_client.get("/api/v1/users/notifications")
    assert response.status_code == HTTP_200_OK
    assert len(response.json()) == 1
