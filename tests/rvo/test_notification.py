from typing import Any

from litestar import Litestar
from litestar.testing import TestClient
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models import Notification, User

from .utils import check_url_when_logged_out


async def test_rvo_test_list_users_when_logged_in(
    test_client: TestClient[Litestar],
    db_session: AsyncSession,
    userinfo: dict[str, Any],
    user: User,
) -> None:
    test_client.set_session_data({"id_token": "fake id token", "userinfo": userinfo})
    response = test_client.get("/rvo")
    assert response.status_code == 200
    assert "/rvo/test" in response.text

    response = test_client.get("/rvo/test")
    assert response.status_code == 200
    assert (
        f'<a href="/rvo/test/user/{user.id}/send-notification">#{user.id} AMI Test User</a>'
        in response.text
    )
    assert "<span>user@example.com, notifications envoyées: 0" in response.text

    assert user.id is not None, "User ID should be set"
    notification_ = Notification(
        user_id=user.id,
        message="Hello notification",
        title="Notification title",
        sender="John Doe",
    )
    db_session.add(notification_)
    await db_session.commit()

    response = test_client.get("/rvo/test")
    assert response.status_code == 200
    assert (
        f'<a href="/rvo/test/user/{user.id}/send-notification">#{user.id} AMI Test User</a>'
        in response.text
    )
    assert "<span>user@example.com, notifications envoyées: 1" in response.text


async def test_rvo_test_list_users_when_logged_out(
    test_client: TestClient[Litestar],
) -> None:
    await check_url_when_logged_out("/rvo/test", test_client)


async def test_rvo_test_send_notification_when_logged_in(
    test_client: TestClient[Litestar],
    db_session: AsyncSession,
    userinfo: dict[str, Any],
    user: User,
) -> None:
    test_client.set_session_data({"id_token": "fake id token", "userinfo": userinfo})
    response = test_client.get(f"/rvo/test/user/{user.id}/send-notification")
    assert response.status_code == 200
    assert "Historique des notifications" not in response.text

    assert user.id is not None, "User ID should be set"
    notification_ = Notification(
        user_id=user.id,
        message="Hello notification",
        title="Notification title",
        sender="John Doe",
    )
    db_session.add(notification_)
    await db_session.commit()
    response = test_client.get(f"/rvo/test/user/{user.id}/send-notification")
    assert response.status_code == 200
    assert "Historique des notifications" in response.text
    assert "Hello notification" in response.text


async def test_rvo_test_send_notification_when_logged_out(
    test_client: TestClient[Litestar],
) -> None:
    await check_url_when_logged_out("/rvo/test/user/0/send-notification", test_client)
