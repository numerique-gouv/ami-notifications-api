import base64
import copy
import datetime
from unittest.mock import Mock

import pytest
from asgiref.sync import sync_to_async
from channels.testing.websocket import WebsocketCommunicator
from pytest_httpx import HTTPXMock
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED

from ami.notification.models import Notification
from ami.partner.models import partners
from ami.tests.utils import get_from_stream
from ami.user.models import Registration, User


@pytest.mark.django_db(transaction=True)
async def test_create_webpush_notification(
    app,
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

    response = await sync_to_async(app.post)(
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
    app,
    settings,
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
    response = app.post("/api/v1/notifications", notification_data, headers=partner_auth)
    assert response.status_code == HTTP_201_CREATED
    assert Notification.objects.count() == 2
    notification2 = Notification.objects.latest("created_at")
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
    assert message.data["app_url"] == settings.PUBLIC_APP_URL


@pytest.mark.django_db
def test_create_notification_dont_try_push(
    app,
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
    response = app.post("/api/v1/notifications", notification_data, headers=partner_auth)
    assert response.status_code == HTTP_201_CREATED
    assert Notification.objects.count() == 1
    notification = Notification.objects.get()
    assert notification.try_push is False
    assert notification.send_status is True
    assert not httpx_mock.get_request()


@pytest.mark.django_db
def test_create_notification_user_does_not_exist(
    app,
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

    monkeypatch.setenv("IGNORE_NOTIFICATION_REQUESTS_FOR_UNREGISTERED_USER", "true")
    response = app.post(
        "/api/v1/notifications", notification_data, headers=partner_auth, status=404
    )
    assert response.json == {"error": "User not found"}
    assert Notification.objects.count() == 0
    user_count = User.objects.count()
    assert user_count == 0

    monkeypatch.setenv("IGNORE_NOTIFICATION_REQUESTS_FOR_UNREGISTERED_USER", "")
    response = app.post("/api/v1/notifications", notification_data, headers=partner_auth)
    assert response.status_code == HTTP_201_CREATED
    assert User.objects.count() == 1
    user = User.objects.get()
    assert user.fc_hash == "unknown_hash"
    assert user.last_logged_in is None
    assert Notification.objects.count() == 1
    notification = Notification.objects.get()
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
    app,
    never_seen_user: User,
    webpush_registration: Registration,
    partner_auth: dict[str, str],
    httpx_mock: HTTPXMock,
    monkeypatch,
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

    monkeypatch.setenv("IGNORE_NOTIFICATION_REQUESTS_FOR_UNREGISTERED_USER", "true")
    response = app.post(
        "/api/v1/notifications", notification_data, headers=partner_auth, status=404
    )
    assert response.json == {"error": "User never seen"}
    assert Notification.objects.count() == 0
    assert User.objects.count() == 1
    user = User.objects.get()
    assert user.fc_hash == never_seen_user.fc_hash
    assert user.last_logged_in is None

    monkeypatch.setenv("IGNORE_NOTIFICATION_REQUESTS_FOR_UNREGISTERED_USER", "")
    response = app.post("/api/v1/notifications", notification_data, headers=partner_auth)
    assert response.status_code == HTTP_201_CREATED
    assert User.objects.count() == 1
    user = User.objects.get()
    assert user.fc_hash == never_seen_user.fc_hash
    assert user.last_logged_in is None
    assert Notification.objects.count() == 1
    notification = Notification.objects.get()
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
    assert notification.partner_id == "psl"
    assert notification.read is False
    assert response.json == {
        "notification_id": str(notification.id),
        "notification_send_status": False,
    }
    assert not httpx_mock.get_request()


@pytest.mark.django_db
def test_create_notification_when_registration_gone(
    app,
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
    response = app.post("/api/v1/notifications", notification_data, headers=partner_auth)
    assert response.status_code == HTTP_201_CREATED
    assert Notification.objects.count() == 1
    assert httpx_mock.get_request()


@pytest.mark.django_db
def test_create_notification_no_registration(
    app,
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
    response = app.post("/api/v1/notifications", notification_data, headers=partner_auth)
    assert response.status_code == HTTP_201_CREATED
    assert Notification.objects.count() == 1
    assert not httpx_mock.get_request()


@pytest.mark.django_db
def test_create_notification_partner_has_no_default_icon(
    app,
    user: User,
    partner_auth: dict[str, str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    partner = copy.deepcopy(partners["psl"])
    partner.icon = ""
    monkeypatch.setattr("ami.partner.auth.partners", {"psl": partner})
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
    response = app.post("/api/v1/notifications", notification_data, headers=partner_auth)
    assert response.status_code == HTTP_201_CREATED
    assert Notification.objects.count() == 1
    notification = Notification.objects.get()
    assert notification.content_icon == "fr-icon-mail-star-line"


@pytest.mark.django_db
def test_create_notification_partner_has_default_icon(
    app,
    user: User,
    partner_auth: dict[str, str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    partner = copy.deepcopy(partners["psl"])
    partner.icon = "fr-icon-megaphone-line"
    monkeypatch.setattr("ami.partner.auth.partners", {"psl": partner})
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
    response = app.post("/api/v1/notifications", notification_data, headers=partner_auth)
    assert response.status_code == HTTP_201_CREATED
    assert Notification.objects.count() == 1
    notification = Notification.objects.get()
    assert notification.content_icon == "fr-icon-megaphone-line"


@pytest.mark.django_db
def test_create_notification_duplicated_payload(
    app,
    user: User,
    partner_auth: dict[str, str],
) -> None:
    notification_data = {
        "recipient_fc_hash": user.fc_hash,
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

    response = app.post("/api/v1/notifications", notification_data, headers=partner_auth)
    assert response.status_code == HTTP_201_CREATED
    assert Notification.objects.count() == 1
    notification = Notification.objects.get()
    assert response.json == {
        "notification_id": str(notification.id),
        "notification_send_status": True,
    }

    # again, same payload
    response = app.post("/api/v1/notifications", notification_data, headers=partner_auth)
    assert response.status_code == HTTP_200_OK
    assert Notification.objects.count() == 1
    assert response.json == {
        "notification_id": str(notification.id),
        "notification_send_status": True,
    }

    # same payload but notification payload exists for another partner
    Notification.objects.all().update(partner_id="foo")
    response = app.post("/api/v1/notifications", notification_data, headers=partner_auth)
    assert response.status_code == HTTP_201_CREATED
    assert Notification.objects.count() == 2
    notification = Notification.objects.latest("created_at")
    assert response.json == {
        "notification_id": str(notification.id),
        "notification_send_status": True,
    }

    # change a random value
    notification_count = Notification.objects.count()
    for key, value in notification_data.items():
        if key == "try_push":
            continue
        data = notification_data.copy()
        if key == "item_generic_status":
            data[key] = "wip"
        else:
            data[key] = value[:-2] + "1" + value[-1]
        send_status = True
        if key == "recipient_fc_hash":
            send_status = False
        response = app.post("/api/v1/notifications", data, headers=partner_auth)
        assert response.status_code == HTTP_201_CREATED
        notification_count += 1
        assert Notification.objects.count() == notification_count
        notification = Notification.objects.latest("created_at")
        assert response.json == {
            "notification_id": str(notification.id),
            "notification_send_status": send_status,
        }
        if key not in [
            "content_icon",
            "item_canal",
            "item_milestone_start_date",
            "item_milestone_end_date",
            "item_external_url",
        ]:
            continue
        del data[key]
        response = app.post("/api/v1/notifications", data, headers=partner_auth)
        assert response.status_code == HTTP_201_CREATED
        notification_count += 1
        assert Notification.objects.count() == notification_count
        notification = Notification.objects.latest("created_at")
        assert response.json == {
            "notification_id": str(notification.id),
            "notification_send_status": send_status,
        }


@pytest.mark.django_db
def test_create_notification_duplicated_payload_with_push(
    app,
    mobile_registration: Registration,
    partner_auth: dict[str, str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    send_mock = Mock()
    monkeypatch.setattr("ami.notification.push.messaging.send", send_mock)
    notification_data = {
        "recipient_fc_hash": mobile_registration.user.fc_hash,
        "item_type": "OTV",
        "item_id": "A-5-JGBJ5VMOY",
        "item_status_label": "Brouillon",
        "item_generic_status": "new",
        "send_date": "2025-11-27T10:55:00.000Z",
        "content_title": "Brouillon de nouvelle demande de démarche d'OTV",
        "content_body": "Merci d'avoir initié votre demande",
    }

    response = app.post("/api/v1/notifications", notification_data, headers=partner_auth)
    assert response.status_code == HTTP_201_CREATED
    assert Notification.objects.count() == 1
    notification = Notification.objects.get()
    assert response.json == {
        "notification_id": str(notification.id),
        "notification_send_status": True,
    }
    send_mock.assert_called_once()

    # again, same payload
    response = app.post("/api/v1/notifications", notification_data, headers=partner_auth)
    assert response.status_code == HTTP_200_OK
    assert Notification.objects.count() == 1
    assert response.json == {
        "notification_id": str(notification.id),
        "notification_send_status": True,
    }
    send_mock.assert_called_once()  # no new call


@pytest.mark.django_db
def test_create_notification_send_ko_with_400_when_required_fields_are_missing(
    app,
    partner_auth: dict[str, str],
) -> None:
    notification_data: dict[str, str] = {}
    response = app.post(
        "/api/v1/notifications", notification_data, headers=partner_auth, status=400
    )
    assert response.json == {
        "content_body": ["Ce champ est obligatoire."],
        "content_title": ["Ce champ est obligatoire."],
        "recipient_fc_hash": ["Ce champ est obligatoire."],
        "send_date": ["Ce champ est obligatoire."],
    }


@pytest.mark.django_db
def test_create_notification_send_ko_with_400_when_required_fields_are_empty(
    app,
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
    response = app.post(
        "/api/v1/notifications", notification_data, headers=partner_auth, status=400
    )
    assert response.json == {
        "content_body": ["Ce champ ne peut être vide."],
        "content_title": ["Ce champ ne peut être vide."],
        "recipient_fc_hash": ["Ce champ ne peut être vide."],
        "send_date": [
            "La date + heure n'a pas le bon format. Utilisez un des formats suivants\xa0: YYYY-MM-DDThh:mm[:ss[.uuuuuu]][+HH:MM|-HH:MM|Z]."
        ],
    }


@pytest.mark.django_db
def test_create_notification_send_ko_with_400_when_required_item_fields_are_missing(
    app,
    user: User,
    partner_auth: dict[str, str],
) -> None:
    item_fields = ["item_type", "item_id", "item_status_label", "item_generic_status"]
    item_optional_fields = [
        "item_canal",
        "item_milestone_start_date",
        "item_milestone_end_date",
        "item_external_url",
    ]
    item_field_values = {
        "item_type": "OTV",
        "item_id": "A-5-JGBJ5VMOY",
        "item_status_label": "Brouillon",
        "item_generic_status": "new",
        "item_milestone_start_date": "2025-12-26T23:00:00.000Z",
        "item_milestone_end_date": "2026-01-02T23:00:00.000Z",
        "item_external_url": "http://otv/a-5-jgbj5vmoy",
        "item_canal": "ami",
    }
    notification_data = {
        "recipient_fc_hash": user.fc_hash,
        "send_date": "2025-11-27T10:55:00.000Z",
        "content_title": "Brouillon de nouvelle demande de démarche d'OTV",
        "content_body": "Merci d'avoir initié votre demande",
    }
    for field in item_fields + item_optional_fields:
        data = {k: v for k, v in notification_data.items()}
        data.update(
            {
                field: item_field_values[field],
            }
        )
        response = app.post("/api/v1/notifications", data, headers=partner_auth, status=400)
        assert response.json == {
            f: ["Ce champ est obligatoire pour une notification associée à un objet."]
            for f in item_fields
            if f != field
        }


@pytest.mark.django_db
def test_create_notification_check_item_milestone_dates(
    app,
    user: User,
    partner_auth: dict[str, str],
) -> None:
    notification_data = {
        "recipient_fc_hash": user.fc_hash,
        "send_date": "2025-11-27T10:55:00.000Z",
        "content_title": "Brouillon de nouvelle demande de démarche d'OTV",
        "content_body": "Merci d'avoir initié votre demande",
        "item_type": "OTV",
        "item_id": "A-5-JGBJ5VMOY",
        "item_status_label": "Brouillon",
        "item_generic_status": "new",
        "item_milestone_start_date": "2025-12-26T23:00:00.000Z",
    }
    response = app.post("/api/v1/notifications", notification_data, headers=partner_auth)
    assert response.status_code == HTTP_201_CREATED
    assert Notification.objects.count() == 1
    notification = Notification.objects.get()
    assert notification.item_milestone_start_date is not None
    assert notification.item_milestone_end_date is None

    notification_data = {
        "recipient_fc_hash": user.fc_hash,
        "send_date": "2025-11-27T10:55:00.000Z",
        "content_title": "Brouillon de nouvelle demande de démarche d'OTV",
        "content_body": "Merci d'avoir initié votre demande",
        "item_type": "OTV",
        "item_id": "A-5-JGBJ5VMOY",
        "item_status_label": "Brouillon",
        "item_generic_status": "new",
        "item_milestone_end_date": "2025-12-26T23:00:00.000Z",
    }
    response = app.post("/api/v1/notifications", notification_data, headers=partner_auth)
    assert response.status_code == HTTP_201_CREATED
    assert Notification.objects.count() == 2
    notification = Notification.objects.latest("created_at")
    assert notification.item_milestone_start_date is None
    assert notification.item_milestone_end_date is not None

    notification_data = {
        "recipient_fc_hash": user.fc_hash,
        "send_date": "2025-11-27T10:55:00.000Z",
        "content_title": "Brouillon de nouvelle demande de démarche d'OTV",
        "content_body": "Merci d'avoir initié votre demande",
        "item_type": "OTV",
        "item_id": "A-5-JGBJ5VMOY",
        "item_status_label": "Brouillon",
        "item_generic_status": "new",
        "item_milestone_start_date": "2025-12-26T23:00:00.001Z",
        "item_milestone_end_date": "2025-12-26T23:00:00.000Z",
    }
    response = app.post(
        "/api/v1/notifications", notification_data, headers=partner_auth, status=400
    )
    assert response.json == {
        "item_milestone_end_date": ["La date de fin doit être supérieure à la date de début."]
    }

    notification_data = {
        "recipient_fc_hash": user.fc_hash,
        "send_date": "2025-11-27T10:55:00.000Z",
        "content_title": "Brouillon de nouvelle demande de démarche d'OTV",
        "content_body": "Merci d'avoir initié votre demande",
        "item_type": "OTV",
        "item_id": "A-5-JGBJ5VMOY",
        "item_status_label": "Brouillon",
        "item_generic_status": "new",
        "item_milestone_start_date": "2025-12-26T23:00:00.000Z",
        "item_milestone_end_date": "2025-12-26T23:00:00.000Z",
    }
    response = app.post("/api/v1/notifications", notification_data, headers=partner_auth)
    assert response.status_code == HTTP_201_CREATED
    assert Notification.objects.count() == 3
    notification = Notification.objects.latest("created_at")
    assert notification.item_milestone_start_date is not None
    assert notification.item_milestone_end_date is not None
    assert notification.item_milestone_start_date == notification.item_milestone_end_date


@pytest.mark.django_db
def test_create_notification_when_optional_fields_are_empty(
    app,
    user: User,
    partner_auth: dict[str, str],
) -> None:
    notification_data = {
        "recipient_fc_hash": user.fc_hash,
        "content_title": "Brouillon de nouvelle demande de démarche d'OTV",
        "content_body": "Merci d'avoir initié votre demande",
        "content_icon": "",
        "item_type": "",
        "item_id": "",
        "item_status_label": "",
        "item_generic_status": "",
        "item_canal": "",
        "item_milestone_start_date": "",
        "item_milestone_end_date": "",
        "item_external_url": "",
        "send_date": "2025-11-27T10:55:00.000Z",
        "try_push": "",
    }
    response = app.post("/api/v1/notifications", notification_data, headers=partner_auth)
    assert response.status_code == HTTP_201_CREATED
    assert Notification.objects.count() == 1
    notification = Notification.objects.get()
    assert notification.user.id == user.id
    assert notification.content_body == "Merci d'avoir initié votre demande"
    assert notification.content_title == "Brouillon de nouvelle demande de démarche d'OTV"
    assert notification.content_icon == "fr-icon-mail-star-line"
    assert notification.item_type is None
    assert notification.item_id is None
    assert notification.item_status_label is None
    assert notification.item_generic_status is None
    assert notification.item_milestone_start_date is None
    assert notification.item_milestone_end_date is None
    assert notification.item_external_url is None
    assert notification.item_canal is None
    assert notification.send_date == datetime.datetime(
        2025, 11, 27, 10, 55, tzinfo=datetime.timezone.utc
    )
    assert notification.partner_id == "psl"
    assert notification.read is False
    assert response.json == {
        "notification_id": str(notification.id),
        "notification_send_status": True,
    }


@pytest.mark.django_db
def test_create_notification_without_auth(app, settings) -> None:
    app.post("/api/v1/notifications", status=401)

    app.post("/api/v1/notifications", headers={"authorization": "foo"}, status=401)

    app.post("/api/v1/notifications", headers={"authorization": "Foo bar"}, status=401)

    app.post("/api/v1/notifications", headers={"authorization": "Basic bar"}, status=401)

    b64 = base64.b64encode(f"foo:{settings.PARTNERS_PSL_SECRET}".encode("utf8")).decode("utf8")
    app.post("/api/v1/notifications", headers={"authorization": f"Basic {b64}"}, status=401)

    b64 = base64.b64encode("psl:foo".encode("utf8")).decode("utf8")
    app.post("/api/v1/notifications", headers={"authorization": f"Basic {b64}"}, status=401)
