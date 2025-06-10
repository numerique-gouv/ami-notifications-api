from litestar import Litestar
from litestar.status_codes import HTTP_200_OK, HTTP_201_CREATED
from litestar.testing import TestClient
from pytest_httpx import HTTPXMock

from app import Notification, Registration


def test_notifications_empty(test_client: TestClient[Litestar]) -> None:
    response = test_client.get("/notifications/test@example.com")
    assert response.status_code == HTTP_200_OK
    assert response.json() == []


async def test_notifications(test_client: TestClient[Litestar], notification: Notification) -> None:
    response = test_client.get(f"/notifications/{notification.email}")
    assert response.status_code == HTTP_200_OK
    assert len(response.json()) == 1
    assert response.json()[0]["email"] == notification.email
    assert response.json()[0]["message"] == notification.message
    assert response.json()[0]["title"] == notification.title
    assert response.json()[0]["sender"] == notification.sender


async def test_create_notification_from_test_and_from_app_context(
    test_client: TestClient[Litestar],
    notification: Notification,
    registration: Registration,
    httpx_mock: HTTPXMock,
) -> None:
    """This test makes sure we're using the same database session in tests and through the API.

    Validate that we can create entries in the database from the test itself (using a fixture)
    and from the API, and both are using the same database session.
    """
    # Make sure we don't even try sending a notification to a push server.
    httpx_mock.add_response(url=registration.subscription["endpoint"])
    notification_data = {
        "email": registration.email,
        "message": "Hello notification 2",
        "title": "Some notification title",
        "sender": "Jane Doe",
    }
    response = test_client.post("/notification/send", json=notification_data)
    assert response.status_code == HTTP_201_CREATED
    response = test_client.get(f"/notifications/{registration.email}")
    assert response.status_code == HTTP_200_OK
    assert len(response.json()) == 2
    assert response.json()[0]["email"] == registration.email
    assert response.json()[0]["message"] == notification.message
    assert response.json()[0]["title"] == notification.title
    assert response.json()[0]["sender"] == notification.sender
    assert response.json()[1]["email"] == registration.email
    assert response.json()[1]["message"] == "Hello notification 2"
    assert response.json()[1]["title"] == "Some notification title"
    assert response.json()[1]["sender"] == "Jane Doe"
