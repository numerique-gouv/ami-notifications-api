import datetime

import pytest
from asgiref.sync import sync_to_async
from channels.testing.websocket import WebsocketCommunicator
from django.core.management import call_command
from django.utils.timezone import now
from pytest_httpx import HTTPXMock

from ami.notification.models import Notification, ScheduledNotification
from ami.partner.models import Partner
from ami.tests.utils import get_from_stream
from ami.user.models import Registration, User


@pytest.mark.django_db(transaction=True)
async def test_command_publish_scheduled_notifications(
    websocket: WebsocketCommunicator,
    webpush_registration: Registration,
    partner: Partner,
    httpx_mock: HTTPXMock,
) -> None:
    user = webpush_registration.user
    httpx_mock.add_response(url=webpush_registration.subscription["endpoint"])

    # no scheduled notifications, no effects
    assert await ScheduledNotification.objects.acount() == 0
    assert await Notification.objects.acount() == 0

    # create some scheduled notifications
    scheduled_notification1 = await ScheduledNotification.objects.acreate(
        user=user,
        content_title="title 1",
        content_body="body 1",
        content_icon="icon 1",
        reference="reference 1",
        internal_url="internal-url-1",
        scheduled_at=now(),
        sent_at=now(),  # already sent
    )
    scheduled_notification2 = await ScheduledNotification.objects.acreate(
        user=user,
        content_title="title 2",
        content_body="body 2",
        content_icon="icon 2",
        reference="reference 2",
        internal_url="internal-url-2",
        scheduled_at=now() + datetime.timedelta(minutes=2),  # too soon
    )
    scheduled_notification3 = await ScheduledNotification.objects.acreate(
        user=user,
        content_title="title 3",
        content_body="body 3",
        content_icon="icon 3",
        reference="reference 3",
        internal_url="internal-url-3",
        scheduled_at=now(),
    )

    await sync_to_async(call_command)("publish-scheduled-notifications")

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
    assert notification.user_id == user.id
    assert notification.content_title == "title 3"
    assert notification.content_body == "body 3"
    assert notification.content_subheading is None
    assert notification.content_icon == "icon 3"
    assert notification.content_link is None
    assert notification.item_type is None
    assert notification.item_id is None
    assert notification.item_parent_partner is None
    assert notification.item_parent_type is None
    assert notification.item_parent_id is None
    assert notification.item_status_label is None
    assert notification.item_generic_status is None
    assert notification.item_milestone_start_date is None
    assert notification.item_milestone_end_date is None
    assert notification.item_canal is None
    assert notification.item_is_archived is None
    assert notification.internal_url == "internal-url-3"
    assert notification.event_date is not None
    assert notification.valid_until is None
    assert notification.partner_id == partner.id
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
def test_command_publish_scheduled_notification_when_registration_gone(
    webpush_registration: Registration,
    partner: Partner,
    httpx_mock: HTTPXMock,
) -> None:
    user = webpush_registration.user
    # Make sure we don't even try sending a notification to a push server.
    httpx_mock.add_response(url=webpush_registration.subscription["endpoint"], status_code=410)

    ScheduledNotification.objects.create(
        user=user,
        content_title="title",
        content_body="body",
        content_icon="icon",
        reference="reference",
        scheduled_at=now(),
    )

    call_command("publish-scheduled-notifications")

    assert Notification.objects.count() == 1
    assert httpx_mock.get_request()


@pytest.mark.django_db
def test_command_publish_scheduled_notification_no_registration(
    user: User,
    partner: Partner,
    httpx_mock: HTTPXMock,
) -> None:
    ScheduledNotification.objects.create(
        user=user,
        content_title="title",
        content_body="body",
        content_icon="icon",
        reference="reference",
        scheduled_at=now(),
    )

    call_command("publish-scheduled-notifications")

    assert Notification.objects.count() == 1
    assert not httpx_mock.get_request()


@pytest.mark.django_db
def test_command_publish_scheduled_notification_never_seen_user(
    never_seen_user: User,
    partner: Partner,
    httpx_mock: HTTPXMock,
) -> None:
    ScheduledNotification.objects.create(
        user=never_seen_user,
        content_title="title",
        content_body="body",
        content_icon="icon",
        reference="reference",
        scheduled_at=now(),
    )

    call_command("publish-scheduled-notifications")

    assert Notification.objects.count() == 1
    notification = Notification.objects.get()
    assert notification.try_push is None
    assert notification.send_status is False
    assert not httpx_mock.get_request()


@pytest.mark.django_db
def test_command_publish_scheduled_notification_duplicated_notification(
    user: User,
    partner: Partner,
    partner_psl: Partner,
    httpx_mock: HTTPXMock,
) -> None:
    # same title, same user, same partner, but for another day
    Notification.objects.create(
        user=user,
        content_title="title",
        partner=partner,
    )
    Notification.objects.all().update(created_at=now() - datetime.timedelta(days=1))
    # other title, same user, same partner
    Notification.objects.create(
        user=user,
        content_title="other title",
        partner=partner,
    )
    # same title, other user, same partner
    other_user = User.objects.create(fc_hash="fc-hash")
    Notification.objects.create(
        user=other_user,
        content_title="title",
        partner=partner,
    )
    # same title, same user, other partner
    Notification.objects.create(
        user=user,
        content_title="title",
        partner=partner_psl,
    )
    ScheduledNotification.objects.create(
        user=user,
        content_title="title",
        content_body="body",
        content_icon="icon",
        reference="reference1",
        scheduled_at=now(),
    )
    ScheduledNotification.objects.create(
        user=user,
        content_title="title",
        content_body="body",
        content_icon="icon",
        reference="reference2",
        scheduled_at=now(),
    )
    old_notification_count = Notification.objects.count()

    call_command("publish-scheduled-notifications")

    # notification created
    assert Notification.objects.count() == old_notification_count + 1
    assert ScheduledNotification.objects.filter(sent_at__isnull=True).exists() is False
    assert not httpx_mock.get_request()

    ScheduledNotification.objects.create(
        user=user,
        content_title="title",
        content_body="body",
        content_icon="icon",
        reference="reference3",
        scheduled_at=now(),
    )

    call_command("publish-scheduled-notifications")

    # notification not created, a notification for this day, title, user, partner, already exists
    assert Notification.objects.count() == old_notification_count + 1
    assert ScheduledNotification.objects.filter(sent_at__isnull=True).exists() is False
    assert not httpx_mock.get_request()
