import base64
import copy
import datetime
from unittest.mock import Mock

import pytest
from asgiref.sync import sync_to_async
from channels.testing.websocket import WebsocketCommunicator
from django.conf import settings
from pytest_httpx import HTTPXMock
from rest_framework.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND

from ami.notification.models import Notification
from ami.partner.models import partners
from ami.tests.utils import get_from_stream
from ami.user.models import Registration, User


@pytest.mark.django_db(transaction=True)
async def test_create_webpush_notification(
    django_app,
    webpush_notification: Notification,
    webpush_registration: Registration,
    partner_auth: dict[str, str],
    httpx_mock: HTTPXMock,
    websocket: WebsocketCommunicator,
) -> None:
    # Make sure we don't even try sending a notification to a push server.
    httpx_mock.add_response(url=webpush_registration.subscription["endpoint"])
    notification_data = {
        "recipient_fc_hash": webpush_registration.user.fc_hash,
        "content_title": "Brouillon de nouvelle demande de démarche d'OTV",
        "content_body": "Merci d'avoir initié votre demande",
        "content_icon": "foo",
        "item_type": "OTV",
        "item_id": "A-5-JGBJ5VMOY",
        "item_status_label": "Brouillon",
        "item_generic_status": "new",
        "item_milestone_start_date": "2025-12-26T23:00:00.000Z",
        "item_milestone_end_date": "2026-01-02T23:00:00.000Z",
        "item_external_url": "http://otv/a-5-jgbj5vmoy",
        "item_canal": "ami",
        "send_date": "2025-11-27T10:55:00.000Z",
        "try_push": True,
    }

    response = await sync_to_async(django_app.post)(
        "/api/v1/notifications", notification_data, headers=partner_auth
    )
    assert response.status_code == HTTP_201_CREATED
    notification_count = await sync_to_async(Notification.objects.count)()
    assert notification_count == 2
    notification2 = await sync_to_async(Notification.objects.select_related("user").get)(
        id=response.json["notification_id"]
    )
    assert notification2.user.id == webpush_registration.user.id
    assert notification2.content_body == "Merci d'avoir initié votre demande"
    assert notification2.content_title == "Brouillon de nouvelle demande de démarche d'OTV"
    assert notification2.content_icon == "foo"
    assert notification2.item_type == "OTV"
    assert notification2.item_id == "A-5-JGBJ5VMOY"
    assert notification2.item_status_label == "Brouillon"
    assert notification2.item_generic_status == "new"
    assert notification2.item_milestone_start_date == datetime.datetime(
        2025, 12, 26, 23, 0, tzinfo=datetime.timezone.utc
    )
    assert notification2.item_milestone_end_date == datetime.datetime(
        2026, 1, 2, 23, 0, tzinfo=datetime.timezone.utc
    )
    assert notification2.item_external_url == "http://otv/a-5-jgbj5vmoy"
    assert notification2.item_canal == "ami"
    assert notification2.send_date == datetime.datetime(
        2025, 11, 27, 10, 55, tzinfo=datetime.timezone.utc
    )
    assert notification2.sender == "PSL"
    assert notification2.partner_id == "psl"
    assert notification2.try_push is True
    assert notification2.send_status is True
    assert notification2.read is False
    assert response.json == {
        "notification_id": str(notification2.id),
        "notification_send_status": True,
    }
    res = await get_from_stream(websocket, 1)
    assert res[0] == {
        "user_id": str(webpush_registration.user.id),
        "id": str(notification2.id),
        "event": "created",
    }
    assert httpx_mock.get_request()


@pytest.mark.django_db
def test_create_mobile_notification(
    django_app,
    mobile_notification: Notification,
    mobile_registration: Registration,
    partner_auth: dict[str, str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    send_mock = Mock()
    monkeypatch.setattr("ami.notification.push.messaging.send", send_mock)
    notification_data = {
        "recipient_fc_hash": mobile_registration.user.fc_hash,
        "content_title": "Brouillon de nouvelle demande de démarche d'OTV",
        "content_body": "Merci d'avoir initié votre demande",
        "content_icon": "foo",
        "item_type": "OTV",
        "item_id": "A-5-JGBJ5VMOY",
        "item_status_label": "Brouillon",
        "item_generic_status": "new",
        "item_milestone_start_date": "2025-12-26T23:00:00.000Z",
        "item_milestone_end_date": "2026-01-02T23:00:00.000Z",
        "item_external_url": "http://otv/a-5-jgbj5vmoy",
        "item_canal": "ami",
        "send_date": "2025-11-27T10:55:00.000Z",
        "try_push": True,
    }
    response = django_app.post("/api/v1/notifications", notification_data, headers=partner_auth)
    assert response.status_code == HTTP_201_CREATED
    all_notifications = Notification.objects.all()
    assert len(all_notifications) == 2
    notification2 = all_notifications[1]
    assert notification2.user.id == mobile_registration.user.id
    assert notification2.content_body == "Merci d'avoir initié votre demande"
    assert notification2.content_title == "Brouillon de nouvelle demande de démarche d'OTV"
    assert notification2.content_icon == "foo"
    assert notification2.item_type == "OTV"
    assert notification2.item_id == "A-5-JGBJ5VMOY"
    assert notification2.item_status_label == "Brouillon"
    assert notification2.item_generic_status == "new"
    assert notification2.item_milestone_start_date == datetime.datetime(
        2025, 12, 26, 23, 0, tzinfo=datetime.timezone.utc
    )
    assert notification2.item_milestone_end_date == datetime.datetime(
        2026, 1, 2, 23, 0, tzinfo=datetime.timezone.utc
    )
    assert notification2.item_external_url == "http://otv/a-5-jgbj5vmoy"
    assert notification2.item_canal == "ami"
    assert notification2.send_date == datetime.datetime(
        2025, 11, 27, 10, 55, tzinfo=datetime.timezone.utc
    )
    assert notification2.sender == "PSL"
    assert notification2.partner_id == "psl"
    assert notification2.try_push is True
    assert notification2.send_status is True
    assert notification2.read is False
    assert response.json == {
        "notification_id": str(notification2.id),
        "notification_send_status": True,
    }

    send_mock.assert_called_once()
    call_args = send_mock.call_args
    message = call_args[0][0]  # First positional argument
    assert message.notification.title == "Brouillon de nouvelle demande de démarche d'OTV"
    assert message.notification.body == "Merci d'avoir initié votre demande"
    assert message.token == mobile_registration.subscription["fcm_token"]


@pytest.mark.django_db
def test_create_notification_dont_try_push(
    django_app,
    webpush_registration: Registration,
    partner_auth: dict[str, str],
    httpx_mock: HTTPXMock,
) -> None:
    notification_data = {
        "recipient_fc_hash": webpush_registration.user.fc_hash,
        "content_title": "Brouillon de nouvelle demande de démarche d'OTV",
        "content_body": "Merci d'avoir initié votre demande",
        "content_icon": "foo",
        "item_type": "OTV",
        "item_id": "A-5-JGBJ5VMOY",
        "item_status_label": "Brouillon",
        "item_generic_status": "new",
        "item_milestone_start_date": "2025-12-26T23:00:00.000Z",
        "item_milestone_end_date": "2026-01-02T23:00:00.000Z",
        "item_external_url": "http://otv/a-5-jgbj5vmoy",
        "item_canal": "ami",
        "send_date": "2025-11-27T10:55:00.000Z",
        "try_push": False,
    }
    response = django_app.post("/api/v1/notifications", notification_data, headers=partner_auth)
    assert response.status_code == HTTP_201_CREATED
    all_notifications = Notification.objects.all()
    assert len(all_notifications) == 1
    notification = all_notifications[0]
    assert notification.try_push is False
    assert notification.send_status is True
    assert not httpx_mock.get_request()


@pytest.mark.django_db
def test_create_notification_user_does_not_exist(
    django_app,
    partner_auth: dict[str, str],
    httpx_mock: HTTPXMock,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    notification_data = {
        "recipient_fc_hash": "unknown_hash",
        "item_type": "OTV",
        "item_id": "A-5-JGBJ5VMOY",
        "item_status_label": "Brouillon",
        "item_generic_status": "new",
        "send_date": "2025-11-27T10:55:00.000Z",
        "content_title": "Brouillon de nouvelle demande de démarche d'OTV",
        "content_body": "Merci d'avoir initié votre demande",
        "content_icon": "foo",
    }

    monkeypatch.setitem(
        settings.CONFIG, "IGNORE_NOTIFICATION_REQUESTS_FOR_UNREGISTERED_USER", "true"
    )
    response = django_app.post(
        "/api/v1/notifications", notification_data, headers=partner_auth, status=404
    )
    assert response.status_code == HTTP_404_NOT_FOUND
    notification_count = Notification.objects.count()
    assert notification_count == 0
    user_count = User.objects.count()
    assert user_count == 0

    monkeypatch.setitem(settings.CONFIG, "IGNORE_NOTIFICATION_REQUESTS_FOR_UNREGISTERED_USER", "")
    response = django_app.post("/api/v1/notifications", notification_data, headers=partner_auth)
    assert response.status_code == HTTP_201_CREATED
    all_users = User.objects.all()
    assert len(all_users) == 1
    user = all_users[0]
    assert user.fc_hash == "unknown_hash"
    assert user.last_logged_in is None
    all_notifications = Notification.objects.all()
    assert len(all_notifications) == 1
    notification = all_notifications[0]
    assert notification.user.id == user.id
    assert notification.content_body == "Merci d'avoir initié votre demande"
    assert notification.content_title == "Brouillon de nouvelle demande de démarche d'OTV"
    assert notification.content_icon == "foo"
    assert notification.item_type == "OTV"
    assert notification.item_id == "A-5-JGBJ5VMOY"
    assert notification.item_status_label == "Brouillon"
    assert notification.item_generic_status == "new"
    assert notification.item_milestone_start_date is None
    assert notification.item_milestone_end_date is None
    assert notification.item_external_url is None
    assert notification.item_canal is None
    assert notification.send_date == datetime.datetime(
        2025, 11, 27, 10, 55, tzinfo=datetime.timezone.utc
    )
    assert notification.sender == "PSL"
    assert notification.partner_id == "psl"
    assert notification.try_push is True
    assert notification.send_status is False
    assert notification.read is False
    assert response.json == {
        "notification_id": str(notification.id),
        "notification_send_status": False,
    }
    assert not httpx_mock.get_request()


@pytest.mark.django_db
def test_create_notification_user_never_seen(
    django_app,
    never_seen_user: User,
    webpush_registration: Registration,
    partner_auth: dict[str, str],
    httpx_mock: HTTPXMock,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    notification_data = {
        "recipient_fc_hash": never_seen_user.fc_hash,
        "item_type": "OTV",
        "item_id": "A-5-JGBJ5VMOY",
        "item_status_label": "Brouillon",
        "item_generic_status": "new",
        "send_date": "2025-11-27T10:55:00.000Z",
        "content_title": "Brouillon de nouvelle demande de démarche d'OTV",
        "content_body": "Merci d'avoir initié votre demande",
        "content_icon": "foo",
    }

    monkeypatch.setitem(
        settings.CONFIG, "IGNORE_NOTIFICATION_REQUESTS_FOR_UNREGISTERED_USER", "true"
    )
    response = django_app.post(
        "/api/v1/notifications", notification_data, headers=partner_auth, status=404
    )
    assert response.status_code == HTTP_404_NOT_FOUND
    notification_count = Notification.objects.count()
    assert notification_count == 0
    all_users = User.objects.all()
    assert len(all_users) == 1
    user = all_users[0]
    assert user.fc_hash == never_seen_user.fc_hash
    assert user.last_logged_in is None

    monkeypatch.setitem(settings.CONFIG, "IGNORE_NOTIFICATION_REQUESTS_FOR_UNREGISTERED_USER", "")
    response = django_app.post("/api/v1/notifications", notification_data, headers=partner_auth)
    assert response.status_code == HTTP_201_CREATED
    all_users = User.objects.all()
    assert len(all_users) == 1
    user = all_users[0]
    assert user.fc_hash == never_seen_user.fc_hash
    assert user.last_logged_in is None
    all_notifications = Notification.objects.all()
    assert len(all_notifications) == 1
    notification = all_notifications[0]
    assert notification.user.id == user.id
    assert notification.content_body == "Merci d'avoir initié votre demande"
    assert notification.content_title == "Brouillon de nouvelle demande de démarche d'OTV"
    assert notification.content_icon == "foo"
    assert notification.item_type == "OTV"
    assert notification.item_id == "A-5-JGBJ5VMOY"
    assert notification.item_status_label == "Brouillon"
    assert notification.item_generic_status == "new"
    assert notification.item_milestone_start_date is None
    assert notification.item_milestone_end_date is None
    assert notification.item_external_url is None
    assert notification.item_canal is None
    assert notification.send_date == datetime.datetime(
        2025, 11, 27, 10, 55, tzinfo=datetime.timezone.utc
    )
    assert notification.sender == "PSL"
    assert notification.partner_id == "psl"
    assert notification.read is False
    assert response.json == {
        "notification_id": str(notification.id),
        "notification_send_status": False,
    }
    assert not httpx_mock.get_request()


@pytest.mark.django_db
def test_create_notification_when_registration_gone(
    django_app,
    webpush_registration: Registration,
    partner_auth: dict[str, str],
    httpx_mock: HTTPXMock,
) -> None:
    """When somebody revokes a PUSH authorization (a push registration), then trying to
    push on this registration will be answered with a status 410 GONE.

    This shouldn't fail the notification process.
    """
    # Make sure we don't even try sending a notification to a push server.
    httpx_mock.add_response(url=webpush_registration.subscription["endpoint"], status_code=410)
    notification_data = {
        "recipient_fc_hash": webpush_registration.user.fc_hash,
        "item_type": "OTV",
        "item_id": "A-5-JGBJ5VMOY",
        "item_status_label": "Brouillon",
        "item_generic_status": "new",
        "send_date": "2025-11-27T10:55:00.000Z",
        "content_title": "Brouillon de nouvelle demande de démarche d'OTV",
        "content_body": "Merci d'avoir initié votre demande",
    }
    response = django_app.post("/api/v1/notifications", notification_data, headers=partner_auth)
    assert response.status_code == HTTP_201_CREATED
    notification_count = Notification.objects.count()
    assert notification_count == 1
    assert httpx_mock.get_request()


@pytest.mark.django_db
def test_create_notification_no_registration(
    django_app,
    user: User,
    partner_auth: dict[str, str],
    httpx_mock: HTTPXMock,
) -> None:
    notification_data = {
        "recipient_fc_hash": user.fc_hash,
        "item_type": "OTV",
        "item_id": "A-5-JGBJ5VMOY",
        "item_status_label": "Brouillon",
        "item_generic_status": "new",
        "send_date": "2025-11-27T10:55:00.000Z",
        "content_title": "Brouillon de nouvelle demande de démarche d'OTV",
        "content_body": "Merci d'avoir initié votre demande",
    }
    response = django_app.post("/api/v1/notifications", notification_data, headers=partner_auth)
    assert response.status_code == HTTP_201_CREATED
    notification_count = Notification.objects.count()
    assert notification_count == 1
    assert not httpx_mock.get_request()


@pytest.mark.django_db
def test_create_notification_partner_has_no_default_icon(
    django_app,
    user: User,
    partner_auth: dict[str, str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    partner = copy.deepcopy(partners["psl"])
    partner.icon = ""
    monkeypatch.setattr("ami.authentication.decorators.partners", {"psl": partner})
    notification_data = {
        "recipient_fc_hash": user.fc_hash,
        "item_type": "OTV",
        "item_id": "A-5-JGBJ5VMOY",
        "item_status_label": "Brouillon",
        "item_generic_status": "new",
        "send_date": "2025-11-27T10:55:00.000Z",
        "content_title": "Brouillon de nouvelle demande de démarche d'OTV",
        "content_body": "Merci d'avoir initié votre demande",
    }
    response = django_app.post("/api/v1/notifications", notification_data, headers=partner_auth)
    assert response.status_code == HTTP_201_CREATED
    all_notifications = Notification.objects.all()
    assert len(all_notifications) == 1
    notification = all_notifications[0]
    assert notification.content_icon == "fr-icon-mail-star-line"


@pytest.mark.django_db
def test_create_notification_partner_has_default_icon(
    django_app,
    user: User,
    partner_auth: dict[str, str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    partner = copy.deepcopy(partners["psl"])
    partner.icon = "fr-icon-megaphone-line"
    monkeypatch.setattr("ami.authentication.decorators.partners", {"psl": partner})
    notification_data = {
        "recipient_fc_hash": user.fc_hash,
        "item_type": "OTV",
        "item_id": "A-5-JGBJ5VMOY",
        "item_status_label": "Brouillon",
        "item_generic_status": "new",
        "send_date": "2025-11-27T10:55:00.000Z",
        "content_title": "Brouillon de nouvelle demande de démarche d'OTV",
        "content_body": "Merci d'avoir initié votre demande",
    }
    response = django_app.post("/api/v1/notifications", notification_data, headers=partner_auth)
    assert response.status_code == HTTP_201_CREATED
    all_notifications = Notification.objects.all()
    assert len(all_notifications) == 1
    notification = all_notifications[0]
    assert notification.content_icon == "fr-icon-megaphone-line"


@pytest.mark.django_db
def test_create_notification_send_ko_with_400_when_required_fields_are_missing(
    django_app,
    partner_auth: dict[str, str],
) -> None:
    notification_data: dict[str, str] = {}
    response = django_app.post(
        "/api/v1/notifications", notification_data, headers=partner_auth, status=400
    )
    assert response.status_code == HTTP_400_BAD_REQUEST
    assert response.json == {
        "content_body": ["This field is required."],
        "content_title": ["This field is required."],
        "item_generic_status": ["This field is required."],
        "item_id": ["This field is required."],
        "item_status_label": ["This field is required."],
        "item_type": ["This field is required."],
        "recipient_fc_hash": ["This field is required."],
        "send_date": ["This field is required."],
    }


@pytest.mark.django_db
def test_create_notification_send_ko_with_400_when_required_fields_are_empty(
    django_app,
    partner_auth: dict[str, str],
) -> None:
    notification_data = {
        "recipient_fc_hash": "",
        "content_title": "",
        "content_body": "",
        "content_icon": "",
        "item_type": "",
        "item_id": "",
        "item_status_label": "",
        "item_generic_status": "",
        "item_canal": "",
        "item_milestone_start_date": "",
        "item_milestone_end_date": "",
        "item_external_url": "",
        "send_date": "",
        "try_push": "",
    }
    response = django_app.post(
        "/api/v1/notifications", notification_data, headers=partner_auth, status=400
    )
    assert response.status_code == HTTP_400_BAD_REQUEST
    assert response.json == {
        "content_body": ["This field may not be blank."],
        "content_title": ["This field may not be blank."],
        "item_generic_status": ['"" is not a valid choice.'],
        "item_id": ["This field may not be blank."],
        "item_status_label": ["This field may not be blank."],
        "item_type": ["This field may not be blank."],
        "recipient_fc_hash": ["This field may not be blank."],
        "send_date": [
            "Datetime has wrong format. Use one of these formats instead: YYYY-MM-DDThh:mm[:ss[.uuuuuu]][+HH:MM|-HH:MM|Z]."
        ],
    }


@pytest.mark.django_db
def test_create_notification_without_auth(django_app) -> None:
    response = django_app.post("/api/v1/notifications", status=401)
    assert response.status_code == 401

    response = django_app.post(
        "/api/v1/notifications", headers={"authorization": "foo"}, status=401
    )
    assert response.status_code == 401

    response = django_app.post(
        "/api/v1/notifications", headers={"authorization": "Foo bar"}, status=401
    )
    assert response.status_code == 401

    response = django_app.post(
        "/api/v1/notifications", headers={"authorization": "Basic bar"}, status=401
    )
    assert response.status_code == 401

    b64 = base64.b64encode(f"foo:{settings.CONFIG['PARTNERS_PSL_SECRET']}".encode("utf8")).decode(
        "utf8"
    )
    response = django_app.post(
        "/api/v1/notifications", headers={"authorization": f"Basic {b64}"}, status=401
    )
    assert response.status_code == 401

    b64 = base64.b64encode("psl:foo".encode("utf8")).decode("utf8")
    response = django_app.post(
        "/api/v1/notifications", headers={"authorization": f"Basic {b64}"}, status=401
    )
    assert response.status_code == 401
