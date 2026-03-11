import base64
import copy
import datetime
import json
from unittest.mock import Mock

import pytest
from litestar import Litestar
from litestar.channels import Subscriber
from litestar.status_codes import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
)
from litestar.testing import TestClient
from pytest_httpx import HTTPXMock
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app import env
from app.models import Notification, Registration, User
from app.partners import partners
from tests.ami.utils import get_from_stream

pytestmark = pytest.mark.skip("skip tests for Django migration")


async def test_create_webpush_notification(
    test_client: TestClient[Litestar],
    notification_events_subscriber: Subscriber,
    app: Litestar,
    db_session: AsyncSession,
    webpush_notification: Notification,
    webpush_registration: Registration,
    partner_auth: dict[str, str],
    httpx_mock: HTTPXMock,
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

    response = test_client.post(
        "/api/v1/notifications", json=notification_data, headers=partner_auth
    )
    assert response.status_code == HTTP_201_CREATED
    all_notifications = (await db_session.execute(select(Notification))).scalars().all()
    assert len(all_notifications) == 2
    notification2 = all_notifications[1]
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
    assert response.json() == {
        "notification_id": str(notification2.id),
        "notification_send_status": True,
    }
    res = await get_from_stream(notification_events_subscriber, 1)
    assert json.loads(res[0].decode()) == {
        "user_id": str(webpush_registration.user.id),
        "id": str(notification2.id),
        "event": "created",
    }
    assert httpx_mock.get_request()


async def test_create_mobile_notification(
    test_client: TestClient[Litestar],
    db_session: AsyncSession,
    mobile_notification: Notification,
    mobile_registration: Registration,
    partner_auth: dict[str, str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    send_mock = Mock()
    monkeypatch.setattr("app.services.notification.messaging.send", send_mock)
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
    response = test_client.post(
        "/api/v1/notifications", json=notification_data, headers=partner_auth
    )
    assert response.status_code == HTTP_201_CREATED
    all_notifications = (await db_session.execute(select(Notification))).scalars().all()
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
    assert response.json() == {
        "notification_id": str(notification2.id),
        "notification_send_status": True,
    }

    send_mock.assert_called_once()
    call_args = send_mock.call_args
    message = call_args[0][0]  # First positional argument
    assert message.notification.title == "Brouillon de nouvelle demande de démarche d'OTV"
    assert message.notification.body == "Merci d'avoir initié votre demande"
    assert message.token == mobile_registration.subscription["fcm_token"]


async def test_create_notification_dont_try_push(
    test_client: TestClient[Litestar],
    db_session: AsyncSession,
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
    response = test_client.post(
        "/api/v1/notifications", json=notification_data, headers=partner_auth
    )
    assert response.status_code == HTTP_201_CREATED
    all_notifications = (await db_session.execute(select(Notification))).scalars().all()
    assert len(all_notifications) == 1
    notification = all_notifications[0]
    assert notification.try_push is False
    assert notification.send_status is True
    assert not httpx_mock.get_request()


async def test_create_notification_user_does_not_exist(
    test_client: TestClient[Litestar],
    db_session: AsyncSession,
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

    monkeypatch.setattr(
        "app.controllers.notification.env.IGNORE_NOTIFICATION_REQUESTS_FOR_UNREGISTERED_USER",
        "true",
    )
    response = test_client.post(
        "/api/v1/notifications", json=notification_data, headers=partner_auth
    )
    assert response.status_code == HTTP_404_NOT_FOUND
    notification_count = (
        await db_session.execute(select(func.count()).select_from(Notification))
    ).scalar()
    assert notification_count == 0
    user_count = (await db_session.execute(select(func.count()).select_from(User))).scalar()
    assert user_count == 0

    monkeypatch.setattr(
        "app.controllers.notification.env.IGNORE_NOTIFICATION_REQUESTS_FOR_UNREGISTERED_USER", ""
    )
    response = test_client.post(
        "/api/v1/notifications", json=notification_data, headers=partner_auth
    )
    assert response.status_code == HTTP_201_CREATED
    all_users = (await db_session.execute(select(User))).scalars().all()
    assert len(all_users) == 1
    user = all_users[0]
    assert user.fc_hash == "unknown_hash"
    assert user.last_logged_in is None
    all_notifications = (await db_session.execute(select(Notification))).scalars().all()
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
    assert response.json() == {
        "notification_id": str(notification.id),
        "notification_send_status": False,
    }
    assert not httpx_mock.get_request()


async def test_create_notification_user_never_seen(
    test_client: TestClient[Litestar],
    db_session: AsyncSession,
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

    monkeypatch.setattr(
        "app.controllers.notification.env.IGNORE_NOTIFICATION_REQUESTS_FOR_UNREGISTERED_USER",
        "true",
    )
    response = test_client.post(
        "/api/v1/notifications", json=notification_data, headers=partner_auth
    )
    assert response.status_code == HTTP_404_NOT_FOUND
    notification_count = (
        await db_session.execute(select(func.count()).select_from(Notification))
    ).scalar()
    assert notification_count == 0
    all_users = (await db_session.execute(select(User))).scalars().all()
    assert len(all_users) == 1
    user = all_users[0]
    assert user.fc_hash == never_seen_user.fc_hash
    assert user.last_logged_in is None

    monkeypatch.setattr(
        "app.controllers.notification.env.IGNORE_NOTIFICATION_REQUESTS_FOR_UNREGISTERED_USER", ""
    )
    response = test_client.post(
        "/api/v1/notifications", json=notification_data, headers=partner_auth
    )
    assert response.status_code == HTTP_201_CREATED
    all_users = (await db_session.execute(select(User))).scalars().all()
    assert len(all_users) == 1
    user = all_users[0]
    assert user.fc_hash == never_seen_user.fc_hash
    assert user.last_logged_in is None
    all_notifications = (await db_session.execute(select(Notification))).scalars().all()
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
    assert response.json() == {
        "notification_id": str(notification.id),
        "notification_send_status": False,
    }
    assert not httpx_mock.get_request()


async def test_create_notification_when_registration_gone(
    test_client: TestClient[Litestar],
    db_session: AsyncSession,
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
    response = test_client.post(
        "/api/v1/notifications", json=notification_data, headers=partner_auth
    )
    assert response.status_code == HTTP_201_CREATED
    notification_count = (
        await db_session.execute(select(func.count()).select_from(Notification))
    ).scalar()
    assert notification_count == 1
    assert httpx_mock.get_request()


async def test_create_notification_no_registration(
    test_client: TestClient[Litestar],
    db_session: AsyncSession,
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
    response = test_client.post(
        "/api/v1/notifications", json=notification_data, headers=partner_auth
    )
    assert response.status_code == HTTP_201_CREATED
    notification_count = (
        await db_session.execute(select(func.count()).select_from(Notification))
    ).scalar()
    assert notification_count == 1
    assert not httpx_mock.get_request()


async def test_create_notification_partner_has_no_default_icon(
    test_client: TestClient[Litestar],
    db_session: AsyncSession,
    user: User,
    partner_auth: dict[str, str],
    httpx_mock: HTTPXMock,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    partner = copy.deepcopy(partners["psl"])
    partner.icon = ""
    monkeypatch.setattr("app.auth.partners", {"psl": partner})
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
    response = test_client.post(
        "/api/v1/notifications", json=notification_data, headers=partner_auth
    )
    assert response.status_code == HTTP_201_CREATED
    all_notifications = (await db_session.execute(select(Notification))).scalars().all()
    assert len(all_notifications) == 1
    notification = all_notifications[0]
    assert notification.content_icon == "fr-icon-mail-star-line"


async def test_create_notification_partner_has_default_icon(
    test_client: TestClient[Litestar],
    db_session: AsyncSession,
    user: User,
    partner_auth: dict[str, str],
    httpx_mock: HTTPXMock,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    partner = copy.deepcopy(partners["psl"])
    partner.icon = "fr-icon-megaphone-line"
    monkeypatch.setattr("app.auth.partners", {"psl": partner})
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
    response = test_client.post(
        "/api/v1/notifications", json=notification_data, headers=partner_auth
    )
    assert response.status_code == HTTP_201_CREATED
    all_notifications = (await db_session.execute(select(Notification))).scalars().all()
    assert len(all_notifications) == 1
    notification = all_notifications[0]
    assert notification.content_icon == "fr-icon-megaphone-line"


async def test_create_notification_send_ko_with_400_when_required_fields_are_missing(
    test_client: TestClient[Litestar],
    partner_auth: dict[str, str],
) -> None:
    notification_data: dict[str, str] = {}
    response = test_client.post(
        "/api/v1/notifications", json=notification_data, headers=partner_auth
    )
    assert response.status_code == HTTP_400_BAD_REQUEST
    assert response.json() == {
        "detail": "Validation failed for POST /api/v1/notifications",
        "extra": [
            {
                "key": "recipient_fc_hash",
                "message": "Field required",
            },
            {
                "key": "content_title",
                "message": "Field required",
            },
            {
                "key": "content_body",
                "message": "Field required",
            },
            {
                "key": "item_type",
                "message": "Field required",
            },
            {
                "key": "item_id",
                "message": "Field required",
            },
            {
                "key": "item_status_label",
                "message": "Field required",
            },
            {
                "key": "item_generic_status",
                "message": "Field required",
            },
            {
                "key": "send_date",
                "message": "Field required",
            },
        ],
        "status_code": 400,
    }


async def test_create_notification_send_ko_with_400_when_required_fields_are_empty(
    test_client: TestClient[Litestar],
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
    response = test_client.post(
        "/api/v1/notifications", json=notification_data, headers=partner_auth
    )
    assert response.status_code == HTTP_400_BAD_REQUEST
    assert response.json() == {
        "detail": "Validation failed for POST /api/v1/notifications",
        "extra": [
            {"message": "String should have at least 1 character", "key": "content_title"},
            {"message": "String should have at least 1 character", "key": "content_body"},
            {"message": "String should have at least 1 character", "key": "content_icon"},
            {"message": "String should have at least 1 character", "key": "item_type"},
            {"message": "String should have at least 1 character", "key": "item_id"},
            {"message": "String should have at least 1 character", "key": "item_status_label"},
            {"message": "Input should be 'new', 'wip' or 'closed'", "key": "item_generic_status"},
            {"message": "String should have at least 1 character", "key": "item_canal"},
            {
                "message": "Input should be a valid datetime or date, input is too short",
                "key": "item_milestone_start_date",
            },
            {
                "message": "Input should be a valid datetime or date, input is too short",
                "key": "item_milestone_end_date",
            },
            {"message": "String should have at least 1 character", "key": "item_external_url"},
            {
                "message": "Input should be a valid datetime or date, input is too short",
                "key": "send_date",
            },
            {
                "message": "Input should be a valid boolean, unable to interpret input",
                "key": "try_push",
            },
        ],
        "status_code": 400,
    }


async def test_create_notification_without_auth(
    test_client: TestClient[Litestar],
) -> None:
    response = test_client.post("/api/v1/notifications")
    assert response.status_code == 401

    response = test_client.post("/api/v1/notifications", headers={"authorization": "foo"})
    assert response.status_code == 401

    response = test_client.post("/api/v1/notifications", headers={"authorization": "Foo bar"})
    assert response.status_code == 401

    response = test_client.post("/api/v1/notifications", headers={"authorization": "Basic bar"})
    assert response.status_code == 401

    b64 = base64.b64encode(f"foo:{env.PARTNERS_PSL_SECRET}".encode("utf8")).decode("utf8")
    response = test_client.post("/api/v1/notifications", headers={"authorization": f"Basic {b64}"})
    assert response.status_code == 401

    b64 = base64.b64encode("psl:foo".encode("utf8")).decode("utf8")
    response = test_client.post("/api/v1/notifications", headers={"authorization": f"Basic {b64}"})
    assert response.status_code == 401


async def test_notification_key(
    test_client: TestClient[Litestar],
) -> None:
    response = test_client.get("/notification-key")
    assert response.status_code == HTTP_200_OK
