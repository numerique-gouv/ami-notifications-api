from litestar import Litestar
from litestar.status_codes import HTTP_200_OK
from litestar.testing import TestClient
from sqlmodel.ext.asyncio.session import AsyncSession

from app import Notification


def test_homepage_title(test_client: TestClient[Litestar]) -> None:
    response = test_client.get("/")
    assert response.status_code == HTTP_200_OK
    assert "<title>Notification test</title>" in response.text


def test_homepage_notifications_empty(
    test_client: TestClient[Litestar], session: AsyncSession
) -> None:
    response = test_client.get("/notifications/test@example.com")
    assert response.status_code == HTTP_200_OK
    assert response.json() == []


async def test_homepage_notifications_one(
    test_client: TestClient[Litestar], session: AsyncSession, notification1: Notification
) -> None:
    response = test_client.get("/notifications/foo@example.com")
    assert response.status_code == HTTP_200_OK
    assert len(response.json()) == 1
    assert response.json()[0]["email"] == "foo@example.com"
    assert response.json()[0]["message"] == "Hello notification 1"
