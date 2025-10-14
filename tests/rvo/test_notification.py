from litestar import Litestar
from litestar.testing import TestClient
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models import Notification, User

from .utils import check_url_when_logged_out


async def test_rvo_test_list_users_when_logged_in(
    test_client: TestClient[Litestar],
    db_session: AsyncSession,
    connected_user: User,
) -> None:
    response = test_client.get("/rvo")
    assert response.status_code == 200
    assert "/rvo/test" in response.text

    response = test_client.get("/rvo/test")
    assert response.status_code == 200
    assert (
        f'<a href="/rvo/test/user/{connected_user.id}/send-notification">#{connected_user.id} AMI Test User</a>'
        in response.text
    )
    assert "<span>user@example.com, notifications envoyées: 0" in response.text

    assert connected_user.id is not None, "User ID should be set"
    notification_ = Notification(
        user_id=connected_user.id,
        message="Hello notification",
        title="Notification title",
        sender="John Doe",
    )
    db_session.add(notification_)
    await db_session.commit()

    response = test_client.get("/rvo/test")
    assert response.status_code == 200
    assert (
        f'<a href="/rvo/test/user/{connected_user.id}/send-notification">#{connected_user.id} AMI Test User</a>'
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
    connected_user: User,
) -> None:
    response = test_client.get(f"/rvo/test/user/{connected_user.id}/send-notification")
    assert response.status_code == 200
    assert "Envoyer une notification à AMI Test User" in response.text
    assert "Historique des notifications" not in response.text

    assert connected_user.id is not None, "User ID should be set"
    notification_ = Notification(
        user_id=connected_user.id,
        message="Hello notification",
        title="Notification title",
        sender="John Doe",
    )
    db_session.add(notification_)
    await db_session.commit()
    response = test_client.get(f"/rvo/test/user/{connected_user.id}/send-notification")
    assert response.status_code == 200
    assert "Historique des notifications" in response.text
    assert "Hello notification" in response.text


async def test_rvo_test_send_notification_when_logged_out(
    test_client: TestClient[Litestar],
) -> None:
    await check_url_when_logged_out("/rvo/test/user/0/send-notification", test_client)
