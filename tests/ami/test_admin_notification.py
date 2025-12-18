import datetime
import uuid

from litestar import Litestar
from litestar.status_codes import (
    HTTP_201_CREATED,
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
)
from litestar.testing import TestClient
from pytest_httpx import HTTPXMock
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Notification, Registration, User


async def test_admin_create_notification_user_does_not_exist(
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


async def test_admin_create_notification_from_test_and_from_app_context(
    test_client: TestClient[Litestar],
    db_session: AsyncSession,
    webpush_notification: Notification,
    webpush_registration: Registration,
    httpx_mock: HTTPXMock,
) -> None:
    """This test makes sure we're using the same database session in tests and through the API.

    Validate that we can create entries in the database from the test itself (using a fixture)
    and from the API, and both are using the same database session.
    """
    # Make sure we don't even try sending a notification to a push server.
    httpx_mock.add_response(url=webpush_registration.subscription["endpoint"])
    notification_data = {
        "user_id": str(webpush_registration.user.id),
        "message": "Hello notification 2",
        "title": "Some notification title",
        "sender": "Jane Doe",
    }
    response = test_client.post("/ami_admin/notifications", json=notification_data)
    assert response.status_code == HTTP_201_CREATED
    all_notifications = (await db_session.execute(select(Notification))).scalars().all()
    assert len(all_notifications) == 2
    notification2 = all_notifications[1]
    assert notification2.user.id == webpush_registration.user.id
    assert notification2.content_body == "Hello notification 2"
    assert notification2.content_title == "Some notification title"
    assert notification2.sender == "Jane Doe"
    assert notification2.read is False
    assert response.json() == {
        "notification_id": str(notification2.id),
        "notification_send_status": True,
    }
    assert httpx_mock.get_request()


async def test_admin_create_notification_test_fields(
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

    # id, created_at, updated_at and read are ignored
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
        "read": True,
    }
    response = test_client.post("/ami_admin/notifications", json=notification_data)
    assert response.status_code == HTTP_201_CREATED

    all_notifications = (await db_session.execute(select(Notification))).scalars().all()
    assert len(all_notifications) == 1
    notification = all_notifications[0]
    assert notification.id != notification_id
    assert notification.created_at < notification_date
    assert notification.updated_at < notification_date
    assert notification.read is False


async def test_admin_create_notification_when_registration_gone(
    test_client: TestClient[Litestar],
    db_session: AsyncSession,
    webpush_registration: Registration,
    httpx_mock: HTTPXMock,
) -> None:
    """When somebody revokes a PUSH authorization (a push registration), then trying to
    push on this registration will be answered with a status 410 GONE.

    This shouldn't fail the notification process.
    """
    # Make sure we don't even try sending a notification to a push server.
    httpx_mock.add_response(url=webpush_registration.subscription["endpoint"], status_code=410)
    notification_data = {
        "user_id": str(webpush_registration.user.id),
        "message": "This will not be PUSHed, but still created on the backend",
        "title": "Some notification title",
        "sender": "Jane Doe",
    }
    response = test_client.post("/ami_admin/notifications", json=notification_data)
    assert response.status_code == HTTP_201_CREATED
    notification_count = (await db_session.execute(select(func.count()).select_from(User))).scalar()
    assert notification_count == 1
    assert httpx_mock.get_request()


async def test_admin_create_notification_no_registration(
    test_client: TestClient[Litestar],
    db_session: AsyncSession,
    user: User,
    httpx_mock: HTTPXMock,
) -> None:
    notification_data = {
        "user_id": str(user.id),
        "message": "This will not be PUSHed, but still created on the backend",
        "title": "Some notification title",
        "sender": "Jane Doe",
    }
    response = test_client.post("/ami_admin/notifications", json=notification_data)
    assert response.status_code == HTTP_201_CREATED
    notification_count = (await db_session.execute(select(func.count()).select_from(User))).scalar()
    assert notification_count == 1
    assert not httpx_mock.get_request()
