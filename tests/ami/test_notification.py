import base64
import copy
import datetime
import uuid
from unittest.mock import Mock

import pytest
from litestar import Litestar
from litestar.exceptions import WebSocketDisconnect
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
from app.auth import jwt_cookie_auth
from app.models import Notification, Registration, User
from app.partners import partners
from tests.ami.utils import assert_query_fails_without_auth, login


async def test_create_webpush_notification(
    test_client: TestClient[Litestar],
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
    assert notification2.read is False
    assert response.json() == {
        "notification_id": str(notification2.id),
        "notification_send_status": True,
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
    monkeypatch.setattr("app.controllers.notification.messaging.send", send_mock)
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
    notification_count = (
        await db_session.execute(select(func.count()).select_from(Notification))
    ).scalar()
    assert notification_count == 1
    assert not httpx_mock.get_request()


async def test_create_notification_user_does_not_exist(
    test_client: TestClient[Litestar],
    db_session: AsyncSession,
    partner_auth: dict[str, str],
    httpx_mock: HTTPXMock,
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
    response = test_client.post(
        "/api/v1/notifications", json=notification_data, headers=partner_auth
    )
    assert response.status_code == HTTP_201_CREATED
    all_users = (await db_session.execute(select(User))).scalars().all()
    assert len(all_users) == 1
    user = all_users[0]
    assert user.fc_hash == "unknown_hash"
    assert user.already_seen is False
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
    response = test_client.post(
        "/api/v1/notifications", json=notification_data, headers=partner_auth
    )
    assert response.status_code == HTTP_201_CREATED
    all_users = (await db_session.execute(select(User))).scalars().all()
    assert len(all_users) == 1
    user = all_users[0]
    assert user.fc_hash == never_seen_user.fc_hash
    assert user.already_seen is False
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


async def test_get_notifications_should_return_empty_list_by_default(
    test_client: TestClient[Litestar], user: User
) -> None:  # The `user` fixture is needed so we don't get a 404 when asking for notifications.
    login(user, test_client)

    response = test_client.get("/api/v1/users/notifications")
    assert response.status_code == HTTP_200_OK
    assert response.json() == []


async def test_get_notifications(
    test_client: TestClient[Litestar],
    db_session: AsyncSession,
    webpush_notification: Notification,
) -> None:
    login(webpush_notification.user, test_client)

    # notification for another user, not returned in notification list of current user
    other_user = User(fc_hash="fc-hash")
    db_session.add(other_user)
    await db_session.commit()
    other_notification = Notification(
        user_id=other_user.id,
        content_body="Other notification",
        content_title="Notification title",
        sender="John Doe",
    )
    db_session.add(other_notification)
    await db_session.commit()

    # test user notification list
    response = test_client.get("/api/v1/users/notifications")
    assert response.status_code == HTTP_200_OK
    assert len(response.json()) == 1
    assert response.json()[0] == {
        "id": str(webpush_notification.id),
        "user_id": str(webpush_notification.user.id),
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
        "created_at": webpush_notification.created_at.isoformat().replace("+00:00", "Z"),
        "read": False,
    }

    response = test_client.get("/api/v1/users/notifications?read=false")
    assert response.status_code == HTTP_200_OK
    assert len(response.json()) == 1
    response = test_client.get("/api/v1/users/notifications?read=true")
    assert response.status_code == HTTP_200_OK
    assert len(response.json()) == 0

    webpush_notification.read = True
    db_session.add(webpush_notification)
    await db_session.commit()

    response = test_client.get("/api/v1/users/notifications")
    assert response.status_code == HTTP_200_OK
    assert len(response.json()) == 1
    assert response.json()[0]["read"] is True

    response = test_client.get("/api/v1/users/notifications?read=false")
    assert response.status_code == HTTP_200_OK
    assert len(response.json()) == 0
    response = test_client.get("/api/v1/users/notifications?read=true")
    assert response.status_code == HTTP_200_OK
    assert len(response.json()) == 1


async def test_get_notifications_without_auth(
    test_client: TestClient[Litestar],
) -> None:
    await assert_query_fails_without_auth("/api/v1/users/notifications", test_client)


async def test_get_notifications_should_return_empty_list_by_default_legacy(
    test_client: TestClient[Litestar], user: User
) -> None:  # The `user` fixture is needed so we don't get a 404 when asking for notifications.
    response = test_client.get(f"/api/v1/users/{user.id}/notifications")
    assert response.status_code == HTTP_200_OK
    assert response.json() == []


async def test_get_notifications_should_return_notifications_for_given_user_id_legacy(
    test_client: TestClient[Litestar],
    db_session: AsyncSession,
    webpush_notification: Notification,
) -> None:
    # notification for another user, not returned in notification list of test user
    other_user = User(fc_hash="fc-hash")
    db_session.add(other_user)
    await db_session.commit()
    other_notification = Notification(
        user_id=other_user.id,
        content_body="Other notification",
        content_title="Notification title",
        sender="John Doe",
    )
    db_session.add(other_notification)
    await db_session.commit()

    # unknown user
    response = test_client.get("/api/v1/users/0/notifications")
    assert response.status_code == HTTP_404_NOT_FOUND

    # test user notification list
    response = test_client.get(f"/api/v1/users/{webpush_notification.user.id}/notifications")
    assert response.status_code == HTTP_200_OK
    assert len(response.json()) == 1
    assert response.json()[0]["user_id"] == str(webpush_notification.user.id)
    assert response.json()[0]["message"] == webpush_notification.content_body
    assert response.json()[0]["title"] == webpush_notification.content_title
    assert response.json()[0]["sender"] == webpush_notification.sender
    assert response.json()[0]["read"] is False

    response = test_client.get(
        f"/api/v1/users/{webpush_notification.user.id}/notifications?read=false"
    )
    assert response.status_code == HTTP_200_OK
    assert len(response.json()) == 1
    response = test_client.get(
        f"/api/v1/users/{webpush_notification.user.id}/notifications?read=true"
    )
    assert response.status_code == HTTP_200_OK
    assert len(response.json()) == 0

    webpush_notification.read = True
    db_session.add(webpush_notification)
    await db_session.commit()

    response = test_client.get(f"/api/v1/users/{webpush_notification.user.id}/notifications")
    assert response.status_code == HTTP_200_OK
    assert len(response.json()) == 1
    assert response.json()[0]["user_id"] == str(webpush_notification.user.id)
    assert response.json()[0]["message"] == webpush_notification.content_body
    assert response.json()[0]["title"] == webpush_notification.content_title
    assert response.json()[0]["sender"] == webpush_notification.sender
    assert response.json()[0]["read"] is True

    response = test_client.get(
        f"/api/v1/users/{webpush_notification.user.id}/notifications?read=false"
    )
    assert response.status_code == HTTP_200_OK
    assert len(response.json()) == 0
    response = test_client.get(
        f"/api/v1/users/{webpush_notification.user.id}/notifications?read=true"
    )
    assert response.status_code == HTTP_200_OK
    assert len(response.json()) == 1


async def test_read_notification(
    test_client: TestClient[Litestar],
    db_session: AsyncSession,
    webpush_notification: Notification,
) -> None:
    login(webpush_notification.user, test_client)

    # notification for another user, can not be patched by test user
    other_user = User(fc_hash="fc-hash")
    db_session.add(other_user)
    await db_session.commit()
    other_notification = Notification(
        user_id=str(other_user.id),
        content_body="Other notification",
        content_title="Notification title",
        sender="John Doe",
    )
    db_session.add(other_notification)
    await db_session.commit()

    # invalid, no payload
    response = test_client.patch(f"/api/v1/users/notification/{uuid.uuid4()}/read")
    assert response.status_code == HTTP_400_BAD_REQUEST

    # unknown notification
    response = test_client.patch(
        f"/api/v1/users/notification/{uuid.uuid4()}/read", json={"read": True}
    )
    assert response.status_code == HTTP_404_NOT_FOUND

    # can not patch notification of another user
    response = test_client.patch(
        f"/api/v1/users/notification/{other_notification.id}/read",
        json={"read": True},
    )
    assert response.status_code == HTTP_404_NOT_FOUND

    # invalid, read is required
    response = test_client.patch(
        f"/api/v1/users/notification/{webpush_notification.id}/read",
        json={"read": None},
    )
    assert response.status_code == HTTP_400_BAD_REQUEST
    assert response.json()["extra"] == [
        {"message": "Input should be a valid boolean", "key": "read"}
    ]

    response = test_client.patch(
        f"/api/v1/users/notification/{webpush_notification.id}/read",
        json={"read": True},
    )
    assert response.status_code == HTTP_200_OK
    assert response.json() == {
        "id": str(webpush_notification.id),
        "user_id": str(webpush_notification.user.id),
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
        "created_at": webpush_notification.created_at.isoformat().replace("+00:00", "Z"),
        "read": True,
    }

    response = test_client.patch(
        f"/api/v1/users/notification/{webpush_notification.id}/read",
        json={"read": False},
    )
    assert response.status_code == HTTP_200_OK
    assert response.json()["read"] is False


async def test_read_notification_without_auth(
    test_client: TestClient[Litestar],
    webpush_notification: Notification,
) -> None:
    await assert_query_fails_without_auth(
        f"/api/v1/users/notification/{webpush_notification.id}/read", test_client, method="patch"
    )


async def test_stream_notification_events_created(
    test_client: TestClient[Litestar],
    db_session: AsyncSession,
    user: User,
) -> None:
    login(user, test_client)

    all_notifications = (await db_session.execute(select(Notification))).scalars().all()
    assert len(all_notifications) == 0

    with test_client.websocket_connect("/api/v1/users/notification/events/stream") as ws:
        try:
            # create a notification
            notification_data = {
                "user_id": str(user.id),
                "message": "Hello notification",
                "title": "Some notification title",
                "sender": "Jane Doe",
            }
            response = test_client.post("/ami_admin/notifications", json=notification_data)
            assert response.status_code == HTTP_201_CREATED
            all_notifications = (await db_session.execute(select(Notification))).scalars().all()
            assert len(all_notifications) == 1
            notification = all_notifications[0]

            # notification event is streamed
            message = ws.receive_json()
            assert message == {
                "id": str(notification.id),
                "user_id": str(user.id),
                "event": "created",
            }
        finally:
            ws.send_text("close")


async def test_stream_notification_events_updated(
    test_client: TestClient[Litestar],
    db_session: AsyncSession,
    webpush_notification: Notification,
) -> None:
    login(webpush_notification.user, test_client)

    all_notifications = (await db_session.execute(select(Notification))).scalars().all()
    assert len(all_notifications) == 1

    with test_client.websocket_connect("/api/v1/users/notification/events/stream") as ws:
        try:
            # create a notification for another user
            other_user = User(fc_hash="fc-hash")
            db_session.add(other_user)
            await db_session.commit()
            notification_data = {
                "user_id": str(other_user.id),
                "message": "Hello other notification",
                "title": "Some notification title",
                "sender": "Jane Doe",
            }
            response = test_client.post("/ami_admin/notifications", json=notification_data)
            assert response.status_code == HTTP_201_CREATED

            # mark user notification as read
            response = test_client.patch(
                f"/api/v1/users/notification/{webpush_notification.id}/read",
                json={"read": True},
            )
            assert response.status_code == HTTP_200_OK

            # only read notification event is streamed: other user notification had no effect for this socket
            message = ws.receive_json()
            assert message == {
                "id": str(webpush_notification.id),
                "user_id": str(webpush_notification.user.id),
                "event": "updated",
            }
        finally:
            ws.send_text("close")


async def test_stream_notification_events_without_auth(
    test_client: TestClient[Litestar],
) -> None:
    with pytest.raises(WebSocketDisconnect):
        with test_client.websocket_connect("/api/v1/users/notification/events/stream"):
            # socket is immediately closed
            pass

    test_client.cookies.update({jwt_cookie_auth.key: "Bearer: bad-value"})
    with pytest.raises(WebSocketDisconnect):
        with test_client.websocket_connect("/api/v1/users/notification/events/stream"):
            # socket is immediately closed
            pass


async def test_notification_key(
    test_client: TestClient[Litestar],
) -> None:
    response = test_client.get("/notification-key")
    assert response.status_code == HTTP_200_OK
