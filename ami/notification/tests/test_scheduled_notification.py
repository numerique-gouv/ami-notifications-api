import datetime

import pytest
from asgiref.sync import sync_to_async
from channels.testing.websocket import WebsocketCommunicator
from django.utils.timezone import now
from pytest_httpx import HTTPXMock

from ami.notification.models import Notification, ScheduledNotification
from ami.tests.utils import get_from_stream
from ami.user.models import Registration, User


@pytest.mark.django_db(transaction=True)
async def test_publish_scheduled_notifications(
    websocket: WebsocketCommunicator,
    webpush_registration: Registration,
    httpx_mock: HTTPXMock,
) -> None:
    user = webpush_registration.user
    httpx_mock.add_response(url=webpush_registration.subscription["endpoint"])

    # no scheduled notifications, no effects
    assert await ScheduledNotification.objects.acount() == 0
    assert await Notification.objects.acount() == 0

    # create some scheduled notifications
    scheduled_notification1 = await ScheduledNotification.objects.acreate(
        user_id=user.id,
        content_title="title 1",
        content_body="body 1",
        content_icon="icon 1",
        reference="reference 1",
        internal_url="internal-url-1",
        scheduled_at=now(),
        sent_at=now(),  # already sent
    )
    scheduled_notification2 = await ScheduledNotification.objects.acreate(
        user_id=user.id,
        content_title="title 2",
        content_body="body 2",
        content_icon="icon 2",
        reference="reference 2",
        internal_url="internal-url-2",
        scheduled_at=now() + datetime.timedelta(minutes=2),  # too soon
    )
    scheduled_notification3 = await ScheduledNotification.objects.acreate(
        user_id=user.id,
        content_title="title 3",
        content_body="body 3",
        content_icon="icon 3",
        reference="reference 3",
        internal_url="internal-url-3",
        scheduled_at=now(),
    )

    await sync_to_async(ScheduledNotification.to_publish.publish)()

    assert await ScheduledNotification.objects.acount() == 3
    assert await Notification.objects.acount() == 1

    await scheduled_notification1.arefresh_from_db()
    await scheduled_notification2.arefresh_from_db()
    await scheduled_notification3.arefresh_from_db()
    assert scheduled_notification1.sent_at is not None
    assert scheduled_notification2.sent_at is None
    assert scheduled_notification3.sent_at is not None

    notification = await Notification.objects.afirst()
    assert notification is not None
    assert notification.user_id == user.id  # type: ignore[attr-defined]
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
    assert notification.internal_url == "internal-url-3"
    assert notification.send_date is not None
    assert notification.partner_id == "dinum-ami"
    assert notification.read is False
    assert notification.try_push is None
    assert notification.send_status is True
    res = await get_from_stream(websocket, 1)
    assert res[0] == {
        "user_id": str(user.id),
        "id": str(notification.id),
        "event": "created",
    }
    assert httpx_mock.get_request()


@pytest.mark.django_db
def test_publish_scheduled_notification_when_registration_gone(
    webpush_registration: Registration,
    httpx_mock: HTTPXMock,
) -> None:
    user = webpush_registration.user
    # Make sure we don't even try sending a notification to a push server.
    httpx_mock.add_response(url=webpush_registration.subscription["endpoint"], status_code=410)

    ScheduledNotification.objects.create(
        user_id=user.id,
        content_title="title",
        content_body="body",
        content_icon="icon",
        reference="reference",
        scheduled_at=now(),
    )

    ScheduledNotification.to_publish.publish()

    notification_count = Notification.objects.count()
    assert notification_count == 1
    assert httpx_mock.get_request()


@pytest.mark.django_db
def test_publish_scheduled_notification_no_registration(
    user: User,
    httpx_mock: HTTPXMock,
) -> None:
    ScheduledNotification.objects.create(
        user_id=user.id,
        content_title="title",
        content_body="body",
        content_icon="icon",
        reference="reference",
        scheduled_at=now(),
    )

    ScheduledNotification.to_publish.publish()

    notification_count = Notification.objects.count()
    assert notification_count == 1
    assert not httpx_mock.get_request()


@pytest.mark.django_db
def test_publish_scheduled_notification_never_seen_user(
    never_seen_user: User,
    httpx_mock: HTTPXMock,
) -> None:
    ScheduledNotification.objects.create(
        user_id=never_seen_user.id,
        content_title="title",
        content_body="body",
        content_icon="icon",
        reference="reference",
        scheduled_at=now(),
    )

    ScheduledNotification.to_publish.publish()

    all_notifications = Notification.objects.all()
    assert len(all_notifications) == 1
    notification = all_notifications[0]
    assert notification.try_push is None
    assert notification.send_status is False
    assert not httpx_mock.get_request()


@pytest.mark.django_db
def test_delete_published_scheduled_notifications(
    user: User,
) -> None:
    scheduled_notification1 = ScheduledNotification.objects.create(
        user_id=user.id,
        content_title="title",
        content_body="body",
        content_icon="icon",
        reference="reference1",
        scheduled_at=now(),
        sent_at=now() - datetime.timedelta(days=6 * 30, minutes=-2),  # too soon
    )
    scheduled_notification2 = ScheduledNotification.objects.create(
        user_id=user.id,
        content_title="title",
        content_body="body",
        content_icon="icon",
        reference="reference2",
        scheduled_at=now(),
        sent_at=None,  # not sent
    )

    ScheduledNotification.objects.create(
        user_id=user.id,
        content_title="title",
        content_body="body",
        content_icon="icon",
        reference="reference3",
        scheduled_at=now(),
        sent_at=now() - datetime.timedelta(days=6 * 30),
    )

    ScheduledNotification.to_delete.delete()

    all_scheduled_notifications = ScheduledNotification.objects.all()
    assert len(all_scheduled_notifications) == 2
    assert all_scheduled_notifications[0].id == scheduled_notification1.id
    assert all_scheduled_notifications[1].id == scheduled_notification2.id
