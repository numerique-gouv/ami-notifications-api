import asyncio
import datetime
import uuid

import pytest
from channels.testing.websocket import WebsocketCommunicator
from pytest_httpx import HTTPXMock
from rest_framework.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND

from ami.notification.models import Notification
from ami.tests.utils import get_from_stream
from ami.user.models import Registration, User


@pytest.mark.django_db
def test_admin_create_notification_user_does_not_exist(
    django_app,
) -> None:
    notification_data = {
        "user_id": str(uuid.uuid4()),
        "message": "Hello notification 2",
        "title": "Some notification title",
        "sender": "Jane Doe",
    }
    response = django_app.post("/ami_admin/notifications", notification_data, status=404)
    assert response.status_code == HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_admin_create_notification_from_test_and_from_app_context(
    django_app,
    webpush_notification: Notification,
    webpush_registration: Registration,
    websocket: WebsocketCommunicator,
    httpx_mock: HTTPXMock,
) -> None:
    """This test makes sure we're using the same database session in tests and through the API.

    Validate that we can create entries in the database from the test itself (using a fixture)
    and from the API, and both are using the same database session.
    """
    # Make sure we don't even try sending a notification to a push server.
    httpx_mock.add_response(url=webpush_registration.subscription["endpoint"])
    notification_data = {
        "user_id": str(webpush_registration.user.id),
        "message": "Hello notification 2",
        "title": "Some notification title",
        "sender": "Jane Doe",
    }
    response = django_app.post("/ami_admin/notifications", notification_data)
    assert response.status_code == HTTP_201_CREATED
    all_notifications = Notification.objects.all()
    assert len(all_notifications) == 2
    notification2 = all_notifications[1]
    assert notification2.user.id == webpush_registration.user.id
    assert notification2.content_body == "Hello notification 2"
    assert notification2.content_title == "Some notification title"
    assert notification2.sender == "Jane Doe"
    assert notification2.partner_id is None
    assert notification2.try_push is None
    assert notification2.send_status is None
    assert notification2.read is False
    assert response.json == {
        "notification_id": str(notification2.id),
        "notification_send_status": True,
    }
    res = asyncio.get_event_loop().run_until_complete(get_from_stream(websocket, 1))
    assert res[0] == {
        "user_id": str(webpush_registration.user.id),
        "id": str(notification2.id),
        "event": "created",
    }
    assert httpx_mock.get_request()


@pytest.mark.django_db
def test_admin_create_notification_test_fields(
    django_app,
    user: User,
) -> None:
    # user_id is required
    notification_data = {
        "user_id": "",
        "message": "Hello !",
        "title": "Some notification title",
        "sender": "Jane Doe",
    }
    response = django_app.post("/ami_admin/notifications", notification_data, status=400)
    assert response.status_code == HTTP_400_BAD_REQUEST
    assert response.json == {"user_id": ["Must be a valid UUID."]}

    # message is required
    notification_data = {
        "user_id": str(user.id),
        "message": "",
        "title": "Some notification title",
        "sender": "Jane Doe",
    }
    response = django_app.post("/ami_admin/notifications", notification_data, status=400)
    assert response.status_code == HTTP_400_BAD_REQUEST
    assert response.json == {"message": ["This field may not be blank."]}

    # id, created_at, updated_at and read are ignored
    notification_date: datetime.datetime = datetime.datetime.now(
        datetime.timezone.utc
    ) + datetime.timedelta(days=1)
    notification_id: uuid.UUID = uuid.uuid4()
    notification_data = {
        "user_id": str(user.id),
        "message": "Hello !",
        "title": "Some notification title",
        "sender": "Jane Doe",
        "id": str(notification_id),
        "created_at": notification_date.isoformat(),
        "updated_at": notification_date.isoformat(),
        "read": True,
    }
    response = django_app.post("/ami_admin/notifications", notification_data)
    assert response.status_code == HTTP_201_CREATED

    all_notifications = Notification.objects.all()
    assert len(all_notifications) == 1
    notification = all_notifications[0]
    assert notification.id != notification_id
    assert notification.created_at < notification_date
    assert notification.updated_at < notification_date
    assert notification.read is False


@pytest.mark.django_db
def test_admin_create_notification_when_registration_gone(
    django_app,
    webpush_registration: Registration,
    httpx_mock: HTTPXMock,
) -> None:
    """When somebody revokes a PUSH authorization (a push registration), then trying to
    push on this registration will be answered with a status 410 GONE.

    This shouldn't fail the notification process.
    """
    # Make sure we don't even try sending a notification to a push server.
    httpx_mock.add_response(url=webpush_registration.subscription["endpoint"], status_code=410)
    notification_data = {
        "user_id": str(webpush_registration.user.id),
        "message": "This will not be PUSHed, but still created on the backend",
        "title": "Some notification title",
        "sender": "Jane Doe",
    }
    response = django_app.post("/ami_admin/notifications", notification_data)
    assert response.status_code == HTTP_201_CREATED
    notification_count = Notification.objects.count()
    assert notification_count == 1
    assert httpx_mock.get_request()


@pytest.mark.django_db
def test_admin_create_notification_no_registration(
    django_app,
    user: User,
    httpx_mock: HTTPXMock,
) -> None:
    notification_data = {
        "user_id": str(user.id),
        "message": "This will not be PUSHed, but still created on the backend",
        "title": "Some notification title",
        "sender": "Jane Doe",
    }
    response = django_app.post("/ami_admin/notifications", notification_data)
    assert response.status_code == HTTP_201_CREATED
    notification_count = Notification.objects.count()
    assert notification_count == 1
    assert not httpx_mock.get_request()
