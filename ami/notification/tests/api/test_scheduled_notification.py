import datetime
import uuid

import pytest
from django.utils.timezone import now

from ami.notification.models import ScheduledNotification
from ami.tests.utils import assert_query_fails_without_auth, login
from ami.user.models import User


@pytest.mark.django_db
def test_create_scheduled_notification(django_app, user: User) -> None:
    login(django_app, user)

    scheduled_notification_date: datetime.datetime = now() + datetime.timedelta(days=1)
    scheduled_notification_data = {
        "content_title": "title",
        "content_body": "body",
        "content_icon": "icon",
        "reference": "reference",
        "internal_url": "internal-url",
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
    assert scheduled_notification.internal_url == "internal-url"
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
        internal_url="internal-url",
        scheduled_at=now(),
        sender="AMI",
    )

    scheduled_notification_date: datetime.datetime = now() + datetime.timedelta(days=1)
    scheduled_notification_data = {
        "content_title": "title-updated",
        "content_body": "body-updated",
        "content_icon": "icon-updated",
        "reference": "reference",
        "internal_url": "internal-url-updated",
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
    scheduled_notification.sent_at = now()
    scheduled_notification.save()

    scheduled_notification_date2: datetime.datetime = now() + datetime.timedelta(days=2)
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
    assert scheduled_notification.internal_url == "internal-url-updated"
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
        scheduled_at=now(),
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
    assert scheduled_notification.internal_url is None
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
        "internal_url": "",
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
    scheduled_notification_date: datetime.datetime = now() + datetime.timedelta(days=1)
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
        scheduled_at=now(),
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
        scheduled_at=now(),
        sender="AMI",
        sent_at=now(),
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
