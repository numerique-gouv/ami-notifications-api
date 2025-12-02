import uuid

import pytest
from litestar import Litestar
from litestar.exceptions import WebSocketDisconnect
from litestar.status_codes import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
    HTTP_500_INTERNAL_SERVER_ERROR,
)
from litestar.testing import TestClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import jwt_cookie_auth
from app.models import Notification, User
from tests.ami.utils import assert_query_fails_without_auth, login


async def test_notify_send_ok_with_200(
    test_client: TestClient[Litestar],
) -> None:
    notification_data = {
        "recipient_fc_hash": "4abd71ec1f581dce2ea2221cbeac7c973c6aea7bcb835acdfe7d6494f1528060",
        "item_type": "OTV",
        "item_id": "A-5-JGBJ5VMOY",
        "item_status_label": "Brouillon",
        "item_generic_status": "new",
        "send_date": "2025-11-27T10:55:00.000Z",
        "content_title": "Brouillon de nouvelle demande de démarche d'OTV",
        "content_body": "Merci d'avoir initié votre demande",
    }
    response = test_client.post("/api/v1/notifications", json=notification_data)
    assert response.status_code == HTTP_201_CREATED
    assert response.json() == {
        "notification_id": "43847a2f-0b26-40a4-a452-8342a99a10a8",
        "notification_send_status": True,
    }


async def test_notify_send_ko_with_200_and_notification_send_status_to_false(
    test_client: TestClient[Litestar],
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
    }
    response = test_client.post("/api/v1/notifications", json=notification_data)
    assert response.status_code == HTTP_201_CREATED
    assert response.json() == {
        "notification_id": "43847a2f-0b26-40a4-a452-8342a99a10a8",
        "notification_send_status": False,
    }


async def test_notify_send_ko_with_400_when_required_fields_are_missing(
    test_client: TestClient[Litestar],
) -> None:
    notification_data: dict[str, str] = {}
    response = test_client.post("/api/v1/notifications", json=notification_data)
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


async def test_notify_send_ko_with_400_when_required_fields_are_empty(
    test_client: TestClient[Litestar],
) -> None:
    notification_data = {
        "recipient_fc_hash": "",
        "item_type": "",
        "item_id": "",
        "item_status_label": "",
        "item_generic_status": "",
        "send_date": "",
        "content_title": "",
        "content_body": "",
    }
    response = test_client.post("/api/v1/notifications", json=notification_data)
    assert response.status_code == HTTP_400_BAD_REQUEST
    assert response.json() == {
        "detail": "Validation failed for POST /api/v1/notifications",
        "extra": [
            {
                "key": "item_generic_status",
                "message": "Input should be 'new', 'wip' or 'closed'",
            },
            {
                "key": "send_date",
                "message": "Input should be a valid datetime or date, input is too short",
            },
        ],
        "status_code": 400,
    }


async def test_notify_send_ko_with_500_when_technical_error(
    test_client: TestClient[Litestar],
) -> None:
    notification_data = {
        "recipient_fc_hash": "technical_error",
        "item_type": "OTV",
        "item_id": "A-5-JGBJ5VMOY",
        "item_status_label": "Brouillon",
        "item_generic_status": "new",
        "send_date": "2025-11-27T10:55:00.000Z",
        "content_title": "Brouillon de nouvelle demande de démarche d'OTV",
        "content_body": "Merci d'avoir initié votre demande",
    }
    response = test_client.post("/api/v1/notifications", json=notification_data)
    assert response.status_code == HTTP_500_INTERNAL_SERVER_ERROR


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
    notification: Notification,
) -> None:
    login(notification.user, test_client)

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
        "send_date": notification.send_date.isoformat().replace("+00:00", "Z"),
        "unread": True,
    }

    response = test_client.get("/api/v1/users/notifications?unread=true")
    assert response.status_code == HTTP_200_OK
    assert len(response.json()) == 1
    response = test_client.get("/api/v1/users/notifications?unread=false")
    assert response.status_code == HTTP_200_OK
    assert len(response.json()) == 0

    notification.unread = False
    db_session.add(notification)
    await db_session.commit()

    response = test_client.get("/api/v1/users/notifications")
    assert response.status_code == HTTP_200_OK
    assert len(response.json()) == 1
    assert response.json()[0]["unread"] is False

    response = test_client.get("/api/v1/users/notifications?unread=true")
    assert response.status_code == HTTP_200_OK
    assert len(response.json()) == 0
    response = test_client.get("/api/v1/users/notifications?unread=false")
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
    notification: Notification,
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
    response = test_client.get(f"/api/v1/users/{notification.user.id}/notifications")
    assert response.status_code == HTTP_200_OK
    assert len(response.json()) == 1
    assert response.json()[0]["user_id"] == str(notification.user.id)
    assert response.json()[0]["message"] == notification.content_body
    assert response.json()[0]["title"] == notification.content_title
    assert response.json()[0]["sender"] == notification.sender
    assert response.json()[0]["unread"] is True

    response = test_client.get(f"/api/v1/users/{notification.user.id}/notifications?unread=true")
    assert response.status_code == HTTP_200_OK
    assert len(response.json()) == 1
    response = test_client.get(f"/api/v1/users/{notification.user.id}/notifications?unread=false")
    assert response.status_code == HTTP_200_OK
    assert len(response.json()) == 0

    notification.unread = False
    db_session.add(notification)
    await db_session.commit()

    response = test_client.get(f"/api/v1/users/{notification.user.id}/notifications")
    assert response.status_code == HTTP_200_OK
    assert len(response.json()) == 1
    assert response.json()[0]["user_id"] == str(notification.user.id)
    assert response.json()[0]["message"] == notification.content_body
    assert response.json()[0]["title"] == notification.content_title
    assert response.json()[0]["sender"] == notification.sender
    assert response.json()[0]["unread"] is False

    response = test_client.get(f"/api/v1/users/{notification.user.id}/notifications?unread=true")
    assert response.status_code == HTTP_200_OK
    assert len(response.json()) == 0
    response = test_client.get(f"/api/v1/users/{notification.user.id}/notifications?unread=false")
    assert response.status_code == HTTP_200_OK
    assert len(response.json()) == 1


async def test_read_notification(
    test_client: TestClient[Litestar],
    db_session: AsyncSession,
    notification: Notification,
) -> None:
    login(notification.user, test_client)

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
        f"/api/v1/users/notification/{notification.id}/read",
        json={"read": None},
    )
    assert response.status_code == HTTP_400_BAD_REQUEST
    assert response.json()["extra"] == [
        {"message": "Input should be a valid boolean", "key": "read"}
    ]

    response = test_client.patch(
        f"/api/v1/users/notification/{notification.id}/read",
        json={"read": True},
    )
    assert response.status_code == HTTP_200_OK
    assert response.json() == {
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
        "send_date": notification.send_date.isoformat().replace("+00:00", "Z"),
        "unread": False,
    }

    response = test_client.patch(
        f"/api/v1/users/notification/{notification.id}/read",
        json={"read": False},
    )
    assert response.status_code == HTTP_200_OK
    assert response.json()["unread"] is True


async def test_read_notification_without_auth(
    test_client: TestClient[Litestar],
    notification: Notification,
) -> None:
    await assert_query_fails_without_auth(
        f"/api/v1/users/notification/{notification.id}/read", test_client, method="patch"
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
    notification: Notification,
) -> None:
    login(notification.user, test_client)

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
                f"/api/v1/users/notification/{notification.id}/read",
                json={"read": True},
            )
            assert response.status_code == HTTP_200_OK

            # only read notification event is streamed: other user notification had no effect for this socket
            message = ws.receive_json()
            assert message == {
                "id": str(notification.id),
                "user_id": str(notification.user.id),
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
