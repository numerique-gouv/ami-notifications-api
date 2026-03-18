import datetime
import uuid

import pytest
from asgiref.sync import sync_to_async
from channels.testing.websocket import WebsocketCommunicator
from pytest_httpx import HTTPXMock

from ami.notification.models import Notification, ScheduledNotification
from ami.tests.utils import assert_query_fails_without_auth, get_from_stream, login
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
        scheduled_at=datetime.datetime.now(datetime.timezone.utc),
        sender="AMI",
        sent_at=datetime.datetime.now(datetime.timezone.utc),  # already sent
    )
    scheduled_notification2 = await ScheduledNotification.objects.acreate(
        user_id=user.id,
        content_title="title 2",
        content_body="body 2",
        content_icon="icon 2",
        reference="reference 2",
        scheduled_at=datetime.datetime.now(datetime.timezone.utc)
        + datetime.timedelta(minutes=2),  # too soon
        sender="AMI",
    )
    scheduled_notification3 = await ScheduledNotification.objects.acreate(
        user_id=user.id,
        content_title="title 3",
        content_body="body 3",
        content_icon="icon 3",
        reference="reference 3",
        scheduled_at=datetime.datetime.now(datetime.timezone.utc),
        sender="AMI",
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
    assert notification.send_date is not None
    assert notification.sender == "AMI"
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
        scheduled_at=datetime.datetime.now(datetime.timezone.utc),
        sender="AMI",
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
        scheduled_at=datetime.datetime.now(datetime.timezone.utc),
        sender="AMI",
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
        scheduled_at=datetime.datetime.now(datetime.timezone.utc),
        sender="AMI",
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
        scheduled_at=datetime.datetime.now(datetime.timezone.utc),
        sender="AMI",
        sent_at=datetime.datetime.now(datetime.timezone.utc)
        - datetime.timedelta(days=6 * 30, minutes=-2),  # too soon
    )
    scheduled_notification2 = ScheduledNotification.objects.create(
        user_id=user.id,
        content_title="title",
        content_body="body",
        content_icon="icon",
        reference="reference2",
        scheduled_at=datetime.datetime.now(datetime.timezone.utc),
        sender="AMI",
        sent_at=None,  # not sent
    )

    ScheduledNotification.objects.create(
        user_id=user.id,
        content_title="title",
        content_body="body",
        content_icon="icon",
        reference="reference3",
        scheduled_at=datetime.datetime.now(datetime.timezone.utc),
        sender="AMI",
        sent_at=datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=6 * 30),
    )

    ScheduledNotification.to_delete.delete()

    all_scheduled_notifications = ScheduledNotification.objects.all()
    assert len(all_scheduled_notifications) == 2
    assert all_scheduled_notifications[0].id == scheduled_notification1.id
    assert all_scheduled_notifications[1].id == scheduled_notification2.id


@pytest.mark.django_db
def test_create_scheduled_notification(django_app, user: User) -> None:
    login(django_app, user)

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
    response = django_app.post(
        "/api/v1/users/scheduled-notifications", scheduled_notification_data, status=201
    )

    assert ScheduledNotification.objects.count() == 1
    scheduled_notification = ScheduledNotification.objects.get()
    assert scheduled_notification.user.id == user.id
    assert scheduled_notification.content_title == "title"
    assert scheduled_notification.content_body == "body"
    assert scheduled_notification.content_icon == "icon"
    assert scheduled_notification.reference == "reference"
    assert scheduled_notification.scheduled_at == scheduled_notification_date
    assert scheduled_notification.sender == "AMI"
    assert scheduled_notification.sent_at is None
    assert response.json == {"scheduled_notification_id": str(scheduled_notification.id)}


@pytest.mark.django_db
def test_create_scheduled_notification_known_reference(django_app, user: User) -> None:
    login(django_app, user)

    scheduled_notification = ScheduledNotification.objects.create(
        user_id=user.id,
        content_title="title",
        content_body="body",
        content_icon="icon",
        reference="reference",
        scheduled_at=datetime.datetime.now(datetime.timezone.utc),
        sender="AMI",
    )

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
    response = django_app.post(
        "/api/v1/users/scheduled-notifications", scheduled_notification_data, status=200
    )
    assert ScheduledNotification.objects.count() == 1
    scheduled_notification.refresh_from_db()
    # scheduled notification was updated
    assert scheduled_notification.user.id == user.id
    assert scheduled_notification.content_title == "title-updated"
    assert scheduled_notification.content_body == "body-updated"
    assert scheduled_notification.content_icon == "icon-updated"
    assert scheduled_notification.reference == "reference"
    assert scheduled_notification.scheduled_at == scheduled_notification_date
    assert scheduled_notification.sender == "AMI"
    assert scheduled_notification.sent_at is None
    assert response.json == {"scheduled_notification_id": str(scheduled_notification.id)}

    # but if scheduled notification is already sent as a notification, changes are ignored
    scheduled_notification.sent_at = datetime.datetime.now(datetime.timezone.utc)
    scheduled_notification.save()

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
    response = django_app.post(
        "/api/v1/users/scheduled-notifications", scheduled_notification_data, status=200
    )
    assert ScheduledNotification.objects.count() == 1
    scheduled_notification.refresh_from_db()
    # scheduled notification was not updated
    assert scheduled_notification.user.id == user.id
    assert scheduled_notification.content_title == "title-updated"
    assert scheduled_notification.content_body == "body-updated"
    assert scheduled_notification.content_icon == "icon-updated"
    assert scheduled_notification.reference == "reference"
    assert scheduled_notification.scheduled_at == scheduled_notification_date
    assert scheduled_notification.sender == "AMI"
    assert scheduled_notification.sent_at is not None
    assert response.json == {"scheduled_notification_id": str(scheduled_notification.id)}

    # same reference for another user: a new scheduled notification is created
    other_user = User.objects.create(fc_hash="fc-hash")
    ScheduledNotification.objects.create(  # Other scheduled notification
        user_id=other_user.id,
        content_title="title",
        content_body="body",
        content_icon="icon",
        reference="other-reference",
        scheduled_at=datetime.datetime.now(datetime.timezone.utc),
        sender="AMI",
    )

    scheduled_notification_data = {
        "content_title": "title",
        "content_body": "body",
        "content_icon": "icon",
        "reference": "other-reference",
        "scheduled_at": scheduled_notification_date.isoformat(),
    }
    response = django_app.post(
        "/api/v1/users/scheduled-notifications", scheduled_notification_data, status=201
    )
    all_scheduled_notifications = ScheduledNotification.objects.all()
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
    assert response.json == {"scheduled_notification_id": str(scheduled_notification.id)}


@pytest.mark.django_db
def test_create_scheduled_notification_test_fields(django_app, user: User) -> None:
    login(django_app, user)

    scheduled_notification_data: dict[str, str] = {}
    response = django_app.post(
        "/api/v1/users/scheduled-notifications", scheduled_notification_data, status=400
    )
    assert response.json == {
        "content_title": ["This field is required."],
        "content_body": ["This field is required."],
        "content_icon": ["This field is required."],
        "reference": ["This field is required."],
        "scheduled_at": ["This field is required."],
    }

    # content_title; content_body, content_icon, reference are required
    scheduled_notification_data = {
        "content_title": "",
        "content_body": "",
        "content_icon": "",
        "reference": "",
    }
    response = django_app.post(
        "/api/v1/users/scheduled-notifications", scheduled_notification_data, status=400
    )
    assert response.json == {
        "content_title": ["This field may not be blank."],
        "content_body": ["This field may not be blank."],
        "content_icon": ["This field may not be blank."],
        "reference": ["This field may not be blank."],
        "scheduled_at": ["This field is required."],
    }

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
    response = django_app.post(
        "/api/v1/users/scheduled-notifications", scheduled_notification_data, status=201
    )

    assert ScheduledNotification.objects.count() == 1
    scheduled_notification = ScheduledNotification.objects.get()
    assert scheduled_notification.id != scheduled_notification_id
    assert scheduled_notification.created_at < scheduled_notification_date
    assert scheduled_notification.updated_at < scheduled_notification_date
    assert scheduled_notification.user.id == user.id
    assert scheduled_notification.sender == "AMI"
    assert scheduled_notification.sent_at is None


@pytest.mark.django_db
def test_create_scheduled_notification_without_auth(django_app) -> None:
    assert_query_fails_without_auth(
        django_app, "/api/v1/users/scheduled-notifications", method="post"
    )


@pytest.mark.django_db
def test_delete_scheduled_notification(django_app, user: User) -> None:
    login(django_app, user)

    ScheduledNotification.objects.create(
        user_id=user.id,
        content_title="title",
        content_body="body",
        content_icon="icon",
        reference="reference",
        scheduled_at=datetime.datetime.now(datetime.timezone.utc),
        sender="AMI",
    )

    django_app.delete(
        "/api/v1/users/scheduled-notifications", {"reference": "reference"}, status=204
    )
    assert ScheduledNotification.objects.count() == 0


@pytest.mark.django_db
def test_delete_scheduled_notification_reference_does_not_exist(django_app, user: User) -> None:
    login(django_app, user)

    django_app.delete("/api/v1/users/scheduled-notifications", {"reference": ""}, status=400)

    django_app.delete(
        "/api/v1/users/scheduled-notifications", {"reference": "reference"}, status=404
    )


@pytest.mark.django_db
def test_delete_scheduled_notification_params(django_app, user: User) -> None:
    login(django_app, user)

    response = django_app.delete("/api/v1/users/scheduled-notifications", status=400)
    assert response.json == {"reference": ["This field is required."]}


@pytest.mark.django_db
def test_delete_scheduled_notification_alread_sent(django_app, user: User) -> None:
    login(django_app, user)

    ScheduledNotification.objects.create(
        user_id=user.id,
        content_title="title",
        content_body="body",
        content_icon="icon",
        reference="reference",
        scheduled_at=datetime.datetime.now(datetime.timezone.utc),
        sender="AMI",
        sent_at=datetime.datetime.now(datetime.timezone.utc),
    )

    django_app.delete(
        "/api/v1/users/scheduled-notifications", {"reference": "reference"}, status=204
    )
    assert ScheduledNotification.objects.count() == 1


@pytest.mark.django_db
def test_delete_scheduled_notification_without_auth(django_app) -> None:
    assert_query_fails_without_auth(
        django_app, "/api/v1/users/scheduled-notifications", method="delete"
    )
