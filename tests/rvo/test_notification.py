import datetime
import uuid

from litestar import Litestar
from litestar.testing import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Notification
from tests.base import ConnectedTestClient

from .utils import check_url_when_logged_out


async def test_rvo_test_list_users_when_logged_in(
    connected_test_client: ConnectedTestClient,
    db_session: AsyncSession,
) -> None:
    connected_user = connected_test_client.user
    response = connected_test_client.get("/rvo")
    assert response.status_code == 200
    assert "/rvo/test" in response.text

    response = connected_test_client.get("/rvo/test")
    assert response.status_code == 200
    assert (
        f'<a href="/rvo/test/user/{connected_user.id}/send-notification">{connected_user.fc_hash}</a>'
        in response.text
    )
    assert "<span>notifications envoyées: 0" in response.text

    notification_ = Notification(
        user_id=str(connected_user.id),
        content_body="Hello notification",
        content_title="Notification title",
        sender="John Doe",
    )
    db_session.add(notification_)
    await db_session.commit()

    response = connected_test_client.get("/rvo/test")
    assert response.status_code == 200
    assert (
        f'<a href="/rvo/test/user/{connected_user.id}/send-notification">{connected_user.fc_hash}</a>'
        in response.text
    )
    assert "<span>notifications envoyées: 1" in response.text


async def test_rvo_test_list_users_when_logged_out(
    test_client: TestClient[Litestar],
) -> None:
    await check_url_when_logged_out("/rvo/test", test_client)


async def test_rvo_test_send_notification_when_logged_in(
    db_session: AsyncSession,
    connected_test_client: ConnectedTestClient,
) -> None:
    connected_user = connected_test_client.user
    response = connected_test_client.get(f"/rvo/test/user/{connected_user.id}/send-notification")
    assert response.status_code == 200
    assert f"Envoyer une notification à {connected_user.fc_hash}" in response.text
    assert "Historique des notifications" not in response.text

    notification_ = Notification(
        user_id=str(connected_user.id),
        content_body="Hello notification1",
        content_title="Notification title",
        sender="John Doe",
    )
    db_session.add(notification_)
    notification_ = Notification(
        user_id=str(connected_user.id),
        content_body="Hello notification2",
        content_title="Notification title",
        sender="John Doe",
        created_at=datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=1),
    )
    db_session.add(notification_)
    await db_session.commit()
    response = connected_test_client.get(f"/rvo/test/user/{connected_user.id}/send-notification")
    assert response.status_code == 200
    assert "Historique des notifications" in response.text
    assert "Hello notification" in response.text
    assert response.text.index("Hello notification1") < response.text.index("Hello notification2")


async def test_rvo_test_send_notification_localtime(
    db_session: AsyncSession,
    connected_test_client: ConnectedTestClient,
) -> None:
    connected_user = connected_test_client.user
    notification = Notification(
        user_id=str(connected_user.id),
        content_body="Hello notification2",
        content_title="Notification title",
        sender="John Doe",
        created_at=datetime.datetime(2025, 11, 14, 11, 0, 0, tzinfo=datetime.timezone.utc),
    )
    db_session.add(notification)
    await db_session.commit()

    response = connected_test_client.get(f"/rvo/test/user/{connected_user.id}/send-notification")
    assert response.status_code == 200
    assert "envoyé par: John Doe, le 14/11/2025 12:00:00" in response.text


async def test_rvo_test_send_notification_when_logged_out(
    test_client: TestClient[Litestar],
) -> None:
    await check_url_when_logged_out(f"/rvo/test/user/{uuid.uuid4()}/send-notification", test_client)
