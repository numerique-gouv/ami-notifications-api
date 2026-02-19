import datetime
import json

from litestar.channels import Subscriber
from pytest_httpx import HTTPXMock
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Notification, Registration, ScheduledNotification, User
from app.services.notification import NotificationService
from app.services.scheduled_notification import ScheduledNotificationService
from tests.ami.utils import get_from_stream
from tests.base import TestClient


async def test_publish_scheduled_notifications(
    test_client: TestClient,
    notification_events_subscriber: Subscriber,
    scheduled_notifications_service: ScheduledNotificationService,
    notifications_service: NotificationService,
    db_session: AsyncSession,
    webpush_registration: Registration,
    httpx_mock: HTTPXMock,
) -> None:
    user = webpush_registration.user
    httpx_mock.add_response(url=webpush_registration.subscription["endpoint"])

    # no scheduled notifications, no effects
    await scheduled_notifications_service.publish_scheduled_notifications(test_client.app)
    scheduled_notification_count = (
        await db_session.execute(select(func.count()).select_from(ScheduledNotification))
    ).scalar()
    assert scheduled_notification_count == 0
    notification_count = (
        await db_session.execute(select(func.count()).select_from(Notification))
    ).scalar()
    assert notification_count == 0

    # create some scheduled notifications
    scheduled_notification1 = ScheduledNotification(
        user_id=user.id,
        content_title="title 1",
        content_body="body 1",
        content_icon="icon 1",
        reference="reference 1",
        scheduled_at=datetime.datetime.now(datetime.timezone.utc),
        sender="AMI",
        sent_at=datetime.datetime.now(datetime.timezone.utc),  # already sent
    )
    db_session.add(scheduled_notification1)
    scheduled_notification2 = ScheduledNotification(
        user_id=user.id,
        content_title="title 2",
        content_body="body 2",
        content_icon="icon 2",
        reference="reference 2",
        scheduled_at=datetime.datetime.now(datetime.timezone.utc)
        + datetime.timedelta(minutes=2),  # too soon
        sender="AMI",
    )
    db_session.add(scheduled_notification2)
    scheduled_notification3 = ScheduledNotification(
        user_id=user.id,
        content_title="title 3",
        content_body="body 3",
        content_icon="icon 3",
        reference="reference 3",
        scheduled_at=datetime.datetime.now(datetime.timezone.utc),
        sender="AMI",
    )
    db_session.add(scheduled_notification3)
    await db_session.commit()

    await scheduled_notifications_service.publish_scheduled_notifications(test_client.app)
    scheduled_notification_count = (
        await db_session.execute(select(func.count()).select_from(ScheduledNotification))
    ).scalar()
    assert scheduled_notification_count == 3
    notification_count = (
        await db_session.execute(select(func.count()).select_from(Notification))
    ).scalar()
    assert notification_count == 1

    await db_session.refresh(scheduled_notification1)
    await db_session.refresh(scheduled_notification2)
    await db_session.refresh(scheduled_notification3)
    assert scheduled_notification1.sent_at is not None
    assert scheduled_notification2.sent_at is None
    assert scheduled_notification3.sent_at is not None

    all_notifications = (await db_session.execute(select(Notification))).scalars().all()
    notification = all_notifications[0]
    assert notification.user.id == user.id
    assert notification.content_title == "title 3"
    assert notification.content_body == "body 3"
    assert notification.content_icon == "icon 3"
    assert notification.item_type is None
    assert notification.item_id is None
    assert notification.item_status_label is None
    assert notification.item_generic_status is None
    assert notification.item_milestone_start_date is None
    assert notification.item_milestone_end_date is None
    assert notification.item_external_url is None
    assert notification.item_canal is None
    assert notification.send_date is not None
    assert notification.sender == "AMI"
    assert notification.read is False
    assert notification.try_push is None
    assert notification.send_status is True
    res = await get_from_stream(notification_events_subscriber, 1)
    assert json.loads(res[0].decode()) == {
        "user_id": str(user.id),
        "id": str(notification.id),
        "event": "created",
    }
    assert httpx_mock.get_request()


async def test_publish_scheduled_notification_when_registration_gone(
    test_client: TestClient,
    scheduled_notifications_service: ScheduledNotificationService,
    notifications_service: NotificationService,
    db_session: AsyncSession,
    webpush_registration: Registration,
    httpx_mock: HTTPXMock,
) -> None:
    user = webpush_registration.user
    # Make sure we don't even try sending a notification to a push server.
    httpx_mock.add_response(url=webpush_registration.subscription["endpoint"], status_code=410)

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

    await scheduled_notifications_service.publish_scheduled_notifications(test_client.app)
    notification_count = (
        await db_session.execute(select(func.count()).select_from(Notification))
    ).scalar()
    assert notification_count == 1
    assert httpx_mock.get_request()


async def test_publish_scheduled_notification_no_registration(
    test_client: TestClient,
    scheduled_notifications_service: ScheduledNotificationService,
    notifications_service: NotificationService,
    db_session: AsyncSession,
    user: User,
    httpx_mock: HTTPXMock,
) -> None:
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

    await scheduled_notifications_service.publish_scheduled_notifications(test_client.app)
    notification_count = (
        await db_session.execute(select(func.count()).select_from(Notification))
    ).scalar()
    assert notification_count == 1
    assert not httpx_mock.get_request()


async def test_publish_scheduled_notification_never_seen_user(
    test_client: TestClient,
    scheduled_notifications_service: ScheduledNotificationService,
    notifications_service: NotificationService,
    db_session: AsyncSession,
    never_seen_user: User,
    httpx_mock: HTTPXMock,
) -> None:
    scheduled_notification = ScheduledNotification(
        user_id=never_seen_user.id,
        content_title="title",
        content_body="body",
        content_icon="icon",
        reference="reference",
        scheduled_at=datetime.datetime.now(datetime.timezone.utc),
        sender="AMI",
    )
    db_session.add(scheduled_notification)
    await db_session.commit()

    await scheduled_notifications_service.publish_scheduled_notifications(test_client.app)
    all_notifications = (await db_session.execute(select(Notification))).scalars().all()
    assert len(all_notifications) == 1
    notification = all_notifications[0]
    assert notification.try_push is None
    assert notification.send_status is False
    assert not httpx_mock.get_request()


async def test_delete_published_scheduled_notifications(
    scheduled_notifications_service: ScheduledNotificationService,
    user: User,
    db_session: AsyncSession,
) -> None:
    scheduled_notification1 = ScheduledNotification(
        user_id=user.id,
        content_title="title",
        content_body="body",
        content_icon="icon",
        reference="reference1",
        scheduled_at=datetime.datetime.now(datetime.timezone.utc),
        sender="AMI",
        sent_at=datetime.datetime.now(datetime.timezone.utc)
        - datetime.timedelta(days=6 * 30, minutes=-2),  # too soon
    )
    db_session.add(scheduled_notification1)
    scheduled_notification2 = ScheduledNotification(
        user_id=user.id,
        content_title="title",
        content_body="body",
        content_icon="icon",
        reference="reference2",
        scheduled_at=datetime.datetime.now(datetime.timezone.utc),
        sender="AMI",
        sent_at=None,  # not sent
    )
    db_session.add(scheduled_notification2)
    scheduled_notification3 = ScheduledNotification(
        user_id=user.id,
        content_title="title",
        content_body="body",
        content_icon="icon",
        reference="reference3",
        scheduled_at=datetime.datetime.now(datetime.timezone.utc),
        sender="AMI",
        sent_at=datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=6 * 30),
    )
    db_session.add(scheduled_notification3)
    await db_session.commit()

    await scheduled_notifications_service.delete_published_scheduled_notifications()

    all_scheduled_notifications = (
        (await db_session.execute(select(ScheduledNotification))).scalars().all()
    )
    assert len(all_scheduled_notifications) == 2
    assert all_scheduled_notifications[0].id == scheduled_notification1.id
    assert all_scheduled_notifications[1].id == scheduled_notification2.id
