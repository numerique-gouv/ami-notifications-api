import datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Notification, ScheduledNotification, User
from app.services.notification import NotificationService
from app.services.scheduled_notification import ScheduledNotificationService


async def test_publish_scheduled_notifications(
    scheduled_notifications_service: ScheduledNotificationService,
    notifications_service: NotificationService,
    db_session: AsyncSession,
    user: User,
) -> None:
    # no scheduled notifications, no effects
    await scheduled_notifications_service.publish_scheduled_notifications()
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

    await scheduled_notifications_service.publish_scheduled_notifications()
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
