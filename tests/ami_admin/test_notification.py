from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Notification
from tests.base import ConnectedTestClient


async def test_ami_admin_test_list_users_when_logged_in(
    connected_test_client: ConnectedTestClient,
    db_session: AsyncSession,
) -> None:
    connected_user = connected_test_client.user
    response = connected_test_client.get("/ami_admin")
    assert response.status_code == 200
    assert "/ami_admin/liste-des-usagers" in response.text

    response = connected_test_client.get("/ami_admin/liste-des-usagers")
    assert response.status_code == 200
    assert "<span>user@example.com, notifications envoyées: 0" in response.text

    notification_ = Notification(
        user_id=str(connected_user.id),
        message="Hello notification",
        title="Notification title",
        sender="John Doe",
    )
    db_session.add(notification_)
    await db_session.commit()

    response = connected_test_client.get("/ami_admin/liste-des-usagers")
    assert response.status_code == 200
    assert "<span>user@example.com, notifications envoyées: 1" in response.text
