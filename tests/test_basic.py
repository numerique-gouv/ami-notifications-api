from typing import Any

from litestar import Litestar
from litestar.status_codes import HTTP_200_OK, HTTP_201_CREATED, HTTP_404_NOT_FOUND
from litestar.testing import TestClient
from pytest_httpx import HTTPXMock
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app import Notification, Registration, User


async def test_notifications_empty(test_client: TestClient[Litestar], user: User) -> None:
    response = test_client.get("/notifications/user@example.com")
    assert response.status_code == HTTP_200_OK
    assert response.json() == []


async def test_notifications(test_client: TestClient[Litestar], notification: Notification) -> None:
    response = test_client.get(f"/notifications/{notification.user.email}")
    assert response.status_code == HTTP_200_OK
    assert len(response.json()) == 1
    assert response.json()[0]["user_id"] == notification.user.id
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
        "user_id": registration.user.id,
        "message": "Hello notification 2",
        "title": "Some notification title",
        "sender": "Jane Doe",
    }
    response = test_client.post("/notification/send", json=notification_data)
    assert response.status_code == HTTP_201_CREATED
    response = test_client.get(f"/notifications/{registration.user.email}")
    assert response.status_code == HTTP_200_OK
    assert len(response.json()) == 2
    assert response.json()[0]["user_id"] == registration.user.id
    assert response.json()[0]["message"] == notification.message
    assert response.json()[0]["title"] == notification.title
    assert response.json()[0]["sender"] == notification.sender
    assert response.json()[1]["user_id"] == registration.user.id
    assert response.json()[1]["message"] == "Hello notification 2"
    assert response.json()[1]["title"] == "Some notification title"
    assert response.json()[1]["sender"] == "Jane Doe"


async def test_database_isolation_test_one(
    test_client: TestClient[Litestar],
    db_session: AsyncSession,
    webpushsubscription: dict[str, Any],
) -> None:
    """Test 1: Create user 'alice@example.com' and verify only this user exists."""
    # Create a user directly in the test database
    user = User(email="alice@example.com")
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    # Create a user using the test client (through the API)
    register_data = {"email": "apiuser@example.com", "subscription": webpushsubscription}
    response = test_client.post("/notification/register", json=register_data)
    assert response.status_code == HTTP_201_CREATED

    # Verify those users exists in our test database
    assert user.id is not None
    assert user.email == "alice@example.com"

    # Verify those users exists through API calls
    response = test_client.get("/notifications/alice@example.com")
    assert response.status_code == HTTP_200_OK
    assert response.json() == []  # User exists (no 404) but has no notifications
    response = test_client.get("/notifications/apiuser@example.com")
    assert response.status_code == HTTP_200_OK
    assert response.json() == []  # User exists (no 404) but has no notifications

    # Check that only those users exists (no leakage from other tests)
    all_users_result = await db_session.exec(select(User))
    all_users_list = list(all_users_result.all())
    assert len(all_users_list) == 2
    assert all_users_list[0].email == "alice@example.com"
    assert all_users_list[1].email == "apiuser@example.com"
    # Importantly, bob@example.com should NOT be here, nor apiuser2@example.com

    # Verify only those users exists through API calls
    response = test_client.get("/notifications/bob@example.com")
    assert response.status_code == HTTP_404_NOT_FOUND
    response = test_client.get("/notifications/apiuser2@example.com")
    assert response.status_code == HTTP_404_NOT_FOUND


async def test_database_isolation_test_two(
    test_client: TestClient[Litestar],
    db_session: AsyncSession,
    webpushsubscription: dict[str, Any],
) -> None:
    """Test 2: Create user 'bob@example.com' and verify only this user exists (no alice)."""
    # Create a different user directly in the test database
    user = User(email="bob@example.com")
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    # Create a user using the test client (through the API)
    register_data = {"email": "apiuser2@example.com", "subscription": webpushsubscription}
    response = test_client.post("/notification/register", json=register_data)
    assert response.status_code == HTTP_201_CREATED

    # Verify those users exists in our test database
    assert user.id is not None
    assert user.email == "bob@example.com"

    # Verify those users exists through API calls
    response = test_client.get("/notifications/bob@example.com")
    assert response.status_code == HTTP_200_OK
    assert response.json() == []  # User exists (no 404) but has no notifications
    response = test_client.get("/notifications/apiuser2@example.com")
    assert response.status_code == HTTP_200_OK
    assert response.json() == []  # User exists (no 404) but has no notifications

    # Check that only those users exists (proving no leakage from test_one)
    all_users_result = await db_session.exec(select(User))
    all_users_list = list(all_users_result.all())
    assert len(all_users_list) == 2
    assert all_users_list[0].email == "bob@example.com"
    assert all_users_list[1].email == "apiuser2@example.com"
    # Importantly, alice@example.com should NOT be here, nor apiuser@example.com

    # Verify only those users exists through API calls
    response = test_client.get("/notifications/alice@example.com")
    assert response.status_code == HTTP_404_NOT_FOUND
    response = test_client.get("/notifications/apiuser@example.com")
    assert response.status_code == HTTP_404_NOT_FOUND
