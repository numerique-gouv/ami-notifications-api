import asyncio
import uuid

import pytest
from channels.testing.websocket import WebsocketCommunicator
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND

from ami.notification.models import Notification
from ami.tests.utils import assert_query_fails_without_auth, get_from_stream, login
from ami.user.models import User


@pytest.mark.django_db
def test_get_notifications_should_return_empty_list_by_default(
    django_app,
    user: User,
) -> None:
    login(django_app, user)

    response = django_app.get("/api/v1/users/notifications")
    assert response.status_code == HTTP_200_OK
    assert response.json == []


@pytest.mark.django_db
def test_get_notifications(
    django_app,
    notification: Notification,
) -> None:
    login(django_app, notification.user)

    # notification for another user, not returned in notification list of current user
    other_user = User.objects.create(fc_hash="fc-hash")
    Notification.objects.create(  # Some other notification
        user_id=other_user.id,
        content_body="Other notification",
        content_title="Notification title",
        sender="John Doe",
    )

    # test user notification list
    response = django_app.get("/api/v1/users/notifications")
    assert response.status_code == HTTP_200_OK
    assert len(response.json) == 1
    assert response.json[0] == {
        "id": str(notification.id),
        "user_id": str(notification.user.id),
        "content_title": "Notification title",
        "content_body": "Hello notification",
        "content_icon": None,
        "sender": "John Doe",
        "item_type": None,
        "item_id": None,
        "item_status_label": None,
        "item_generic_status": None,
        "item_canal": None,
        "item_milestone_start_date": None,
        "item_milestone_end_date": None,
        "item_external_url": None,
        "created_at": notification.created_at.isoformat().replace("+00:00", "Z"),
        "read": False,
    }

    response = django_app.get("/api/v1/users/notifications?read=false")
    assert response.status_code == HTTP_200_OK
    assert len(response.json) == 1
    response = django_app.get("/api/v1/users/notifications?read=true")
    assert response.status_code == HTTP_200_OK
    assert len(response.json) == 0

    notification.read = True
    notification.save()

    response = django_app.get("/api/v1/users/notifications")
    assert response.status_code == HTTP_200_OK
    assert len(response.json) == 1
    assert response.json[0]["read"] is True

    response = django_app.get("/api/v1/users/notifications?read=false")
    assert response.status_code == HTTP_200_OK
    assert len(response.json) == 0
    response = django_app.get("/api/v1/users/notifications?read=true")
    assert response.status_code == HTTP_200_OK
    assert len(response.json) == 1


@pytest.mark.django_db
def test_get_notifications_without_auth(django_app) -> None:
    assert_query_fails_without_auth(django_app, "/api/v1/users/notifications")


@pytest.mark.django_db
def test_read_notification(
    django_app,
    notification: Notification,
    websocket: WebsocketCommunicator,
) -> None:
    login(django_app, notification.user)

    # notification for another user, can not be patched by test user
    other_user = User.objects.create(fc_hash="fc-hash")
    other_notification = Notification.objects.create(
        user_id=str(other_user.id),
        content_body="Other notification",
        content_title="Notification title",
        sender="John Doe",
    )

    # invalid, no payload
    response = django_app.patch(f"/api/v1/users/notification/{uuid.uuid4()}/read", status=400)
    assert response.status_code == HTTP_400_BAD_REQUEST

    # unknown notification
    response = django_app.patch(
        f"/api/v1/users/notification/{uuid.uuid4()}/read", {"read": "True"}, status=404
    )
    assert response.status_code == HTTP_404_NOT_FOUND

    # can not patch notification of another user
    response = django_app.patch(
        f"/api/v1/users/notification/{other_notification.id}/read", {"read": True}, status=404
    )
    assert response.status_code == HTTP_404_NOT_FOUND

    # invalid, read is required
    response = django_app.patch(
        f"/api/v1/users/notification/{notification.id}/read", {"read": None}, status=400
    )
    assert response.status_code == HTTP_400_BAD_REQUEST
    assert response.json == {"read": ["Must be a valid boolean."]}

    response = django_app.patch(
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
        "sender": "John Doe",
        "item_type": None,
        "item_id": None,
        "item_status_label": None,
        "item_generic_status": None,
        "item_canal": None,
        "item_milestone_start_date": None,
        "item_milestone_end_date": None,
        "item_external_url": None,
        "created_at": notification.created_at.isoformat().replace("+00:00", "Z"),
        "read": True,
    }
    res = asyncio.get_event_loop().run_until_complete(get_from_stream(websocket, 1))
    assert res[0] == {
        "user_id": str(notification.user.id),
        "id": str(notification.id),
        "event": "updated",
    }

    response = django_app.patch(
        f"/api/v1/users/notification/{notification.id}/read",
        {"read": False},
    )
    assert response.status_code == HTTP_200_OK
    assert response.json["read"] is False


@pytest.mark.django_db
def test_read_notification_without_auth(
    django_app,
    notification: Notification,
) -> None:
    assert_query_fails_without_auth(
        django_app,
        f"/api/v1/users/notification/{notification.id}/read",
        method="patch",
    )


async def test_notification_key(
    django_app,
    settings,
) -> None:
    settings.CONFIG["VAPID_APPLICATION_SERVER_KEY"] = "some-application-key"
    response = django_app.get("/notification-key", status=200)
    assert response.text == "some-application-key"
