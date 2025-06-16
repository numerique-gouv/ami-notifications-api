from litestar import Litestar
from litestar.status_codes import HTTP_200_OK, HTTP_201_CREATED
from litestar.testing import TestClient
from pytest_httpx import HTTPXMock

from app import Notification, Registration, User


async def test_notifications_empty(test_client: TestClient[Litestar]) -> None:
    response = test_client.get("/notifications/test@example.com")
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


async def test_database_isolation_test_one(test_client: TestClient[Litestar], db_session) -> None:
    """Test 1: Create user 'alice@example.com' and verify only this user exists."""
    # Create a user directly in the test database
    user = User(email="alice@example.com")
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    # Verify this user exists in our test database
    assert user.id is not None
    assert user.email == "alice@example.com"

    # Check that only this user exists (no leakage from other tests)
    from sqlalchemy import select

    all_users = await db_session.exec(select(User))
    all_users_list = all_users.all()
    assert len(all_users_list) == 1
    assert all_users_list[0][0].email == "alice@example.com"


async def test_database_isolation_test_two(test_client: TestClient[Litestar], db_session) -> None:
    """Test 2: Create user 'bob@example.com' and verify only this user exists (no alice)."""
    # Create a different user directly in the test database
    user = User(email="bob@example.com")
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    # Verify this user exists in our test database
    assert user.id is not None
    assert user.email == "bob@example.com"

    # Check that only this user exists (proving no leakage from test_one)
    from sqlalchemy import select

    all_users = await db_session.exec(select(User))
    all_users_list = all_users.all()
    assert len(all_users_list) == 1
    assert all_users_list[0][0].email == "bob@example.com"
    # Importantly, alice@example.com should NOT be here


async def test_shared_database_api_and_test_engine(
    test_client: TestClient[Litestar], db_session, webpushsubscription
) -> None:
    """Test that API and test engine share the same database (as discovered)."""

    # 1. Create a user via the API
    register_data = {"email": "apiuser@example.com", "subscription": webpushsubscription}
    response = test_client.post("/notification/register", json=register_data)
    assert response.status_code == HTTP_201_CREATED

    # 2. Create a user directly in the test database
    test_user = User(email="testuser@example.com")
    db_session.add(test_user)
    await db_session.commit()
    await db_session.refresh(test_user)

    # 3. Verify both users exist in the test database (shared with API)
    from sqlalchemy import select

    all_users = await db_session.exec(select(User))
    all_users_list = all_users.all()
    assert len(all_users_list) == 2
    users = [row[0] for row in all_users_list]
    emails = {user.email for user in users}
    assert emails == {"apiuser@example.com", "testuser@example.com"}

    # 4. Verify API user exists via API calls
    response = test_client.get("/notifications/apiuser@example.com")
    assert response.status_code == HTTP_200_OK
    assert response.json() == []  # User exists (no 404) but has no notifications

    # 5. Verify test user is also accessible via API (shared database)
    response = test_client.get("/notifications/testuser@example.com")
    assert response.status_code == HTTP_200_OK
    assert response.json() == []  # User exists, no notifications

    # 6. Create a notification for the API-created user via test database
    api_user = next(user for user in users if user.email == "apiuser@example.com")
    notification = Notification(
        user_id=api_user.id,
        message="Test message from test engine",
        title="Test Title",
        sender="Test Sender",
    )
    db_session.add(notification)
    await db_session.commit()

    # 7. Verify this notification is visible via API (proving shared database)
    response = test_client.get("/notifications/apiuser@example.com")
    assert response.status_code == HTTP_200_OK
    notifications = response.json()
    assert len(notifications) == 1
    assert notifications[0]["message"] == "Test message from test engine"
    assert notifications[0]["title"] == "Test Title"
    assert notifications[0]["sender"] == "Test Sender"
