import asyncio
import datetime
import uuid

import pytest
from channels.testing.websocket import WebsocketCommunicator
from django.utils.timezone import now
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND

from ami.notification.models import Notification
from ami.tests.utils import assert_query_fails_without_auth, get_from_stream, login
from ami.user.models import User


@pytest.mark.django_db
def test_get_notifications_should_return_empty_list_by_default(
    app,
    user: User,
) -> None:
    login(app, user)

    response = app.get("/api/v1/users/notifications")
    assert response.status_code == HTTP_200_OK
    assert response.json == []


@pytest.mark.django_db
def test_get_notifications(
    app,
    settings,
    notification: Notification,
) -> None:
    login(app, notification.user)

    notification.item_generic_status = "new"
    notification.item_status_label = "Nouveau"
    notification.item_type = "OperationTranquilliteVacances"
    notification.item_id = "42"
    notification.partner_id = "psl"
    notification.content_link = "http://external-url"
    notification.internal_url = "internal-url"
    notification.save()

    other_notification = Notification.objects.create(
        user=notification.user,
        content_body="Other notification",
        content_private_body="some private body content",
        content_title="Notification title",
        valid_until=now() + datetime.timedelta(seconds=1),
    )

    # notification for another user, not returned in notification list of current user
    other_user = User.objects.create(fc_hash="fc-hash")
    Notification.objects.create(  # Some other notification
        user_id=other_user.id,
        content_body="Other notification",
        content_title="Notification title",
    )

    # notification with outdated valid_until
    Notification.objects.create(
        user=notification.user,
        content_body="Other notification",
        content_title="Notification title",
        valid_until=now(),
    )

    # test user notification list
    response = app.get("/api/v1/users/notifications")
    assert response.status_code == HTTP_200_OK
    assert len(response.json) == 2
    assert response.json[0] == {
        "id": str(other_notification.id),
        "user_id": str(other_notification.user.id),
        "content_title": "Notification title",
        "content_body": "Other notification some private body content",
        "content_icon": None,
        "item_type": None,
        "item_id": None,
        "item_status_label": None,
        "item_generic_status": None,
        "item_canal": None,
        "item_milestone_start_date": None,
        "item_milestone_end_date": None,
        "url": None,
        "created_at": other_notification.created_at.isoformat().replace("+00:00", "Z"),
        "read": False,
    }
    assert response.json[1] == {
        "id": str(notification.id),
        "user_id": str(notification.user.id),
        "content_title": "Notification title",
        "content_body": "Hello notification",
        "content_icon": "fr-icon-mail-fill",
        "item_type": "OperationTranquilliteVacances",
        "item_id": "42",
        "item_status_label": "Nouveau",
        "item_generic_status": "new",
        "item_canal": None,
        "item_milestone_start_date": None,
        "item_milestone_end_date": None,
        "url": f"{settings.PUBLIC_APP_URL}/#/requests",
        "created_at": notification.created_at.isoformat().replace("+00:00", "Z"),
        "read": False,
    }


@pytest.mark.django_db
def test_get_notifications_icon(
    app,
    settings,
    notification: Notification,
) -> None:
    login(app, notification.user)

    # PSL has no default icon
    Notification.objects.create(
        user=notification.user,
        content_body="Notification",
        content_title="Notification title",
        content_icon="icon-psl",
        partner_id="psl",
    )
    Notification.objects.create(
        user=notification.user,
        content_body="Notification",
        content_title="Notification title",
        partner_id="psl",
    )
    Notification.objects.create(
        user=notification.user,
        content_body="Notification",
        content_title="Notification title",
        content_icon="icon-psl-event",
        item_generic_status="new",
        item_status_label="Nouveau",
        item_type="OperationTranquilliteVacances",
        item_id="42",
        partner_id="psl",
    )
    for status in ["new", "wip", "closed"]:
        Notification.objects.create(
            user=notification.user,
            content_body="Notification",
            content_title="Notification title",
            item_generic_status=status,
            item_status_label="Label",
            item_type="OperationTranquilliteVacances",
            item_id="42",
            partner_id="psl",
        )
    # missing content item field
    for field in ["item_generic_status", "item_status_label", "item_type", "item_id"]:
        data = {
            "user": notification.user,
            "content_body": "Notification",
            "content_title": "Notification title",
            "item_generic_status": "new",
            "item_status_label": "Nouveau",
            "item_type": "OperationTranquilliteVacances",
            "item_id": "42",
            "partner_id": "psl",
        }
        data.pop(field)
        Notification.objects.create(**data)

    # DINUM AMI as default icon
    Notification.objects.create(
        user=notification.user,
        content_body="Notification",
        content_title="Notification title",
        content_icon="icon-dinum-ami",
        partner_id="dinum-ami",
    )
    Notification.objects.create(
        user=notification.user,
        content_body="Notification",
        content_title="Notification title",
        partner_id="dinum-ami",
    )
    Notification.objects.create(
        user=notification.user,
        content_body="Notification",
        content_title="Notification title",
        content_icon="icon-dinum-ami-event",
        item_generic_status="new",
        item_status_label="Nouveau",
        item_type="JeDéménage",
        item_id="42",
        partner_id="dinum-ami",
    )
    for status in ["new", "wip", "closed"]:
        Notification.objects.create(
            user=notification.user,
            content_body="Notification",
            content_title="Notification title",
            item_generic_status=status,
            item_status_label="Label",
            item_type="JeDéménage",
            item_id="42",
            partner_id="dinum-ami",
        )
    # missing content item field
    for field in ["item_generic_status", "item_status_label", "item_type", "item_id"]:
        data = {
            "user": notification.user,
            "content_body": "Notification",
            "content_title": "Notification title",
            "item_generic_status": "new",
            "item_status_label": "Nouveau",
            "item_type": "JeDéménage",
            "item_id": "42",
            "partner_id": "dinum-ami",
        }
        data.pop(field)
        Notification.objects.create(**data)

    response = app.get("/api/v1/users/notifications")
    assert [r["content_icon"] for r in response.json] == [
        "fr-icon-smartphone-line",
        "fr-icon-smartphone-line",
        "fr-icon-smartphone-line",
        "fr-icon-smartphone-line",
        "fr-icon-flag-fill",
        "fr-icon-eye-fill",
        "fr-icon-mail-fill",
        "icon-dinum-ami-event",
        "fr-icon-smartphone-line",
        "icon-dinum-ami",
        "fr-icon-mail-star-line",
        "fr-icon-mail-star-line",
        "fr-icon-mail-star-line",
        "fr-icon-mail-star-line",
        "fr-icon-flag-fill",
        "fr-icon-eye-fill",
        "fr-icon-mail-fill",
        "icon-psl-event",
        "fr-icon-mail-star-line",
        "icon-psl",
        None,
    ]


@pytest.mark.django_db
def test_get_notifications_without_auth(app) -> None:
    assert_query_fails_without_auth(app, "/api/v1/users/notifications")


@pytest.mark.django_db
def test_read_notification(
    app,
    notification: Notification,
    websocket: WebsocketCommunicator,
) -> None:
    login(app, notification.user)

    # notification for another user, can not be patched by test user
    other_user = User.objects.create(fc_hash="fc-hash")
    other_notification = Notification.objects.create(
        user_id=str(other_user.id),
        content_body="Other notification",
        content_title="Notification title",
    )

    # invalid, no payload
    response = app.patch(f"/api/v1/users/notification/{uuid.uuid4()}/read", status=400)
    assert response.status_code == HTTP_400_BAD_REQUEST

    # unknown notification
    response = app.patch(
        f"/api/v1/users/notification/{uuid.uuid4()}/read", {"read": "True"}, status=404
    )
    assert response.status_code == HTTP_404_NOT_FOUND

    # can not patch notification of another user
    response = app.patch(
        f"/api/v1/users/notification/{other_notification.id}/read", {"read": True}, status=404
    )
    assert response.status_code == HTTP_404_NOT_FOUND

    # invalid, read is required
    response = app.patch(
        f"/api/v1/users/notification/{notification.id}/read", {"read": None}, status=400
    )
    assert response.status_code == HTTP_400_BAD_REQUEST
    assert response.json == {"read": ["Must be a valid boolean."]}

    response = app.patch(
        f"/api/v1/users/notification/{notification.id}/read",
        {"read": True},
    )
    assert response.status_code == HTTP_200_OK
    assert response.json == {
        "id": str(notification.id),
        "user_id": str(notification.user.id),
        "content_title": "Notification title",
        "content_body": "Hello notification",
        "content_icon": None,
        "item_type": None,
        "item_id": None,
        "item_status_label": None,
        "item_generic_status": None,
        "item_canal": None,
        "item_milestone_start_date": None,
        "item_milestone_end_date": None,
        "url": None,
        "created_at": notification.created_at.isoformat().replace("+00:00", "Z"),
        "read": True,
    }
    res = asyncio.get_event_loop().run_until_complete(get_from_stream(websocket, 1))
    assert res[0] == {
        "user_id": str(notification.user.id),
        "id": str(notification.id),
        "event": "updated",
    }

    response = app.patch(
        f"/api/v1/users/notification/{notification.id}/read",
        {"read": False},
    )
    assert response.status_code == HTTP_200_OK
    assert response.json["read"] is False


@pytest.mark.django_db
def test_read_notification_without_auth(
    app,
    notification: Notification,
) -> None:
    assert_query_fails_without_auth(
        app,
        f"/api/v1/users/notification/{notification.id}/read",
        method="patch",
    )


async def test_notification_key(
    app,
    settings,
) -> None:
    settings.VAPID_APPLICATION_SERVER_KEY = "some-application-key"
    response = app.get("/notification-key", status=200)
    assert response.text == "some-application-key"
