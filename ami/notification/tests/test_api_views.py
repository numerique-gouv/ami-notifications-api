import pytest
from rest_framework.status import HTTP_200_OK

from ami.notification.models import Notification
from ami.tests.utils import assert_query_fails_without_auth, login
from ami.user.models import User


@pytest.mark.django_db
def test_get_notifications_should_return_empty_list_by_default(
    django_app,
    user: User,
) -> None:  # The `user` fixture is needed so we don't get a 404 when asking for notifications.
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
    other_user = User(fc_hash="fc-hash")
    other_user.save()
    other_notification = Notification(
        user_id=other_user.id,
        content_body="Other notification",
        content_title="Notification title",
        sender="John Doe",
    )
    other_notification.save()

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
