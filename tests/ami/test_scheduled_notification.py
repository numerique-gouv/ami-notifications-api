import datetime
import uuid

from litestar import Litestar
from litestar.status_codes import HTTP_200_OK, HTTP_201_CREATED, HTTP_400_BAD_REQUEST
from litestar.testing import TestClient
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import ScheduledNotification, User
from tests.ami.utils import assert_query_fails_without_auth, login


async def test_create_scheduled_notification(
    test_client: TestClient[Litestar],
    db_session: AsyncSession,
    user: User,
) -> None:
    login(user, test_client)

    scheduled_notification_date: datetime.datetime = datetime.datetime.now(
        datetime.timezone.utc
    ) + datetime.timedelta(days=1)
    scheduled_notification_data = {
        "content_title": "title",
        "content_body": "body",
        "content_icon": "icon",
        "reference": "reference",
        "scheduled_at": scheduled_notification_date.isoformat(),
    }
    response = test_client.post(
        "/api/v1/users/scheduled-notifications", json=scheduled_notification_data
    )
    assert response.status_code == HTTP_201_CREATED

    all_scheduled_notifications = (
        (await db_session.execute(select(ScheduledNotification))).scalars().all()
    )
    assert len(all_scheduled_notifications) == 1
    scheduled_notification = all_scheduled_notifications[0]
    assert scheduled_notification.user.id == user.id
    assert scheduled_notification.content_title == "title"
    assert scheduled_notification.content_body == "body"
    assert scheduled_notification.content_icon == "icon"
    assert scheduled_notification.reference == "reference"
    assert scheduled_notification.scheduled_at == scheduled_notification_date
    assert scheduled_notification.sender == "AMI"
    assert scheduled_notification.sent_at is None
    assert response.json() == {"scheduled_notification_id": str(scheduled_notification.id)}


async def test_create_scheduled_notification_known_reference(
    test_client: TestClient[Litestar],
    db_session: AsyncSession,
    user: User,
) -> None:
    login(user, test_client)

    scheduled_notification = ScheduledNotification(
        user_id=user.id,
        content_title="title",
        content_body="body",
        content_icon="icon",
        reference="reference",
        scheduled_at=datetime.datetime.now(datetime.timezone.utc),
        sender="AMI",
    )
    db_session.add(scheduled_notification)
    await db_session.commit()

    scheduled_notification_date: datetime.datetime = datetime.datetime.now(
        datetime.timezone.utc
    ) + datetime.timedelta(days=1)
    scheduled_notification_data = {
        "content_title": "title-updated",
        "content_body": "body-updated",
        "content_icon": "icon-updated",
        "reference": "reference",
        "scheduled_at": scheduled_notification_date.isoformat(),
    }
    response = test_client.post(
        "/api/v1/users/scheduled-notifications", json=scheduled_notification_data
    )
    assert response.status_code == HTTP_200_OK
    scheduled_notification_count = (
        await db_session.execute(select(func.count()).select_from(ScheduledNotification))
    ).scalar()
    assert scheduled_notification_count == 1
    await db_session.refresh(scheduled_notification)
    # scheduled notification was updated
    assert scheduled_notification.user.id == user.id
    assert scheduled_notification.content_title == "title-updated"
    assert scheduled_notification.content_body == "body-updated"
    assert scheduled_notification.content_icon == "icon-updated"
    assert scheduled_notification.reference == "reference"
    assert scheduled_notification.scheduled_at == scheduled_notification_date
    assert scheduled_notification.sender == "AMI"
    assert scheduled_notification.sent_at is None
    assert response.json() == {"scheduled_notification_id": str(scheduled_notification.id)}

    # but if scheduled notification is already sent as a notification, changes are ignored
    scheduled_notification.sent_at = datetime.datetime.now(datetime.timezone.utc)
    db_session.add(scheduled_notification)
    await db_session.commit()

    scheduled_notification_date2: datetime.datetime = datetime.datetime.now(
        datetime.timezone.utc
    ) + datetime.timedelta(days=2)
    scheduled_notification_data = {
        "content_title": "title-updated-again",
        "content_body": "body-updated-again",
        "content_icon": "icon-updated-again",
        "reference": "reference",
        "scheduled_at": scheduled_notification_date2.isoformat(),
    }
    response = test_client.post(
        "/api/v1/users/scheduled-notifications", json=scheduled_notification_data
    )
    assert response.status_code == HTTP_200_OK
    scheduled_notification_count = (
        await db_session.execute(select(func.count()).select_from(ScheduledNotification))
    ).scalar()
    assert scheduled_notification_count == 1
    await db_session.refresh(scheduled_notification)
    # scheduled notification was not updated
    assert scheduled_notification.user.id == user.id
    assert scheduled_notification.content_title == "title-updated"
    assert scheduled_notification.content_body == "body-updated"
    assert scheduled_notification.content_icon == "icon-updated"
    assert scheduled_notification.reference == "reference"
    assert scheduled_notification.scheduled_at == scheduled_notification_date
    assert scheduled_notification.sender == "AMI"
    assert scheduled_notification.sent_at is not None
    assert response.json() == {"scheduled_notification_id": str(scheduled_notification.id)}

    # same reference for another user: a new scheduled notification is created
    other_user = User(fc_hash="fc-hash")
    db_session.add(other_user)
    await db_session.commit()
    other_scheduled_notification = ScheduledNotification(
        user_id=other_user.id,
        content_title="title",
        content_body="body",
        content_icon="icon",
        reference="other-reference",
        scheduled_at=datetime.datetime.now(datetime.timezone.utc),
        sender="AMI",
    )
    db_session.add(other_scheduled_notification)
    await db_session.commit()

    scheduled_notification_data = {
        "content_title": "title",
        "content_body": "body",
        "content_icon": "icon",
        "reference": "other-reference",
        "scheduled_at": scheduled_notification_date.isoformat(),
    }
    response = test_client.post(
        "/api/v1/users/scheduled-notifications", json=scheduled_notification_data
    )
    assert response.status_code == HTTP_201_CREATED
    all_scheduled_notifications = (
        (await db_session.execute(select(ScheduledNotification))).scalars().all()
    )
    assert len(all_scheduled_notifications) == 3
    scheduled_notification = all_scheduled_notifications[2]
    assert scheduled_notification.user.id == user.id
    assert scheduled_notification.content_title == "title"
    assert scheduled_notification.content_body == "body"
    assert scheduled_notification.content_icon == "icon"
    assert scheduled_notification.reference == "other-reference"
    assert scheduled_notification.scheduled_at == scheduled_notification_date
    assert scheduled_notification.sender == "AMI"
    assert scheduled_notification.sent_at is None
    assert response.json() == {"scheduled_notification_id": str(scheduled_notification.id)}


async def test_create_scheduled_notification_test_fields(
    test_client: TestClient[Litestar],
    db_session: AsyncSession,
    user: User,
) -> None:
    login(user, test_client)

    scheduled_notification_data: dict[str, str] = {}
    response = test_client.post(
        "/api/v1/users/scheduled-notifications", json=scheduled_notification_data
    )
    assert response.status_code == HTTP_400_BAD_REQUEST
    assert response.json()["extra"] == [
        {"message": "Field required", "key": "content_title"},
        {"message": "Field required", "key": "content_body"},
        {"message": "Field required", "key": "content_icon"},
        {"message": "Field required", "key": "reference"},
        {"message": "Field required", "key": "scheduled_at"},
    ]

    # content_title; content_body, content_icon, reference are required
    scheduled_notification_data = {
        "content_title": "",
        "content_body": "",
        "content_icon": "",
        "reference": "",
    }
    response = test_client.post(
        "/api/v1/users/scheduled-notifications", json=scheduled_notification_data
    )
    assert response.status_code == HTTP_400_BAD_REQUEST
    assert response.json()["extra"] == [
        {"message": "String should have at least 1 character", "key": "content_title"},
        {"message": "String should have at least 1 character", "key": "content_body"},
        {"message": "String should have at least 1 character", "key": "content_icon"},
        {"message": "String should have at least 1 character", "key": "reference"},
        {"message": "Field required", "key": "scheduled_at"},
    ]

    # id, created_at, updated_at, user_id, sender and sent_at are ignored
    scheduled_notification_date: datetime.datetime = datetime.datetime.now(
        datetime.timezone.utc
    ) + datetime.timedelta(days=1)
    scheduled_notification_id: uuid.UUID = uuid.uuid4()
    scheduled_notification_data = {
        "content_title": "title",
        "content_body": "body",
        "content_icon": "icon",
        "reference": "reference",
        "scheduled_at": scheduled_notification_date.isoformat(),
        "id": str(scheduled_notification_id),
        "created_at": scheduled_notification_date.isoformat(),
        "updated_at": scheduled_notification_date.isoformat(),
        "user_id": str(uuid.uuid4()),
        "sender": "sender",
        "sent_at": scheduled_notification_date.isoformat(),
    }
    response = test_client.post(
        "/api/v1/users/scheduled-notifications", json=scheduled_notification_data
    )
    assert response.status_code == HTTP_201_CREATED

    all_scheduled_notifications = (
        (await db_session.execute(select(ScheduledNotification))).scalars().all()
    )
    assert len(all_scheduled_notifications) == 1
    scheduled_notification = all_scheduled_notifications[0]
    assert scheduled_notification.id != scheduled_notification_id
    assert scheduled_notification.created_at < scheduled_notification_date
    assert scheduled_notification.updated_at < scheduled_notification_date
    assert scheduled_notification.user.id == user.id
    assert scheduled_notification.sender == "AMI"
    assert scheduled_notification.sent_at is None


async def test_create_scheduled_notification_without_auth(
    test_client: TestClient[Litestar],
) -> None:
    await assert_query_fails_without_auth(
        "/api/v1/users/scheduled-notifications", test_client, method="post"
    )
