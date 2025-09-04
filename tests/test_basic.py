import datetime
import uuid
from typing import Any, cast
from urllib.parse import urlencode

import pytest
from litestar import Litestar
from litestar.status_codes import HTTP_200_OK, HTTP_201_CREATED, HTTP_404_NOT_FOUND
from litestar.testing import TestClient
from pytest_httpx import HTTPXMock
from sqlalchemy.orm import InstrumentedAttribute, selectinload
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app import Notification, Registration, User

FAKE_USERINFO = {
    "sub": "fake sub",
    "given_name": "Angela Claire Louise",
    "given_name_array": ["Angela", "Claire", "Louise"],
    "family_name": "DUBOIS",
    "birthdate": "1962-08-24",
    "gender": "female",
    "aud": "fake aud",
    "exp": 1753877658,
    "iat": 1753877598,
    "iss": "https://fcp-low.sbx.dev-franceconnect.fr/api/v2",
}


async def test_notifications_empty(
    test_client: TestClient[Litestar], user: User
) -> None:  # The `user` fixture is needed so we don't get a 404 when asking for notifications.
    response = test_client.get(f"/api/v1/users/{user.id}/notifications")
    assert response.status_code == HTTP_200_OK
    assert response.json() == []


async def test_notifications(test_client: TestClient[Litestar], notification: Notification) -> None:
    response = test_client.get(f"/api/v1/users/{notification.user.id}/notifications")
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
    response = test_client.post("/api/v1/notifications", json=notification_data)
    assert response.status_code == HTTP_201_CREATED
    response = test_client.get(f"/api/v1/users/{registration.user.id}/notifications")
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
    response = test_client.post("/api/v1/registrations", json=register_data)
    assert response.status_code == HTTP_201_CREATED

    # Verify those users exists in our test database
    assert user.id is not None
    assert user.id == 1
    assert user.email == "alice@example.com"

    # Verify those users exists through API calls
    response = test_client.get(f"/api/v1/users/{user.id}/notifications")
    assert response.status_code == HTTP_200_OK
    assert response.json() == []  # User exists (no 404) but has no notifications
    response = test_client.get("/api/v1/users/2/notifications")
    assert response.status_code == HTTP_200_OK
    assert response.json() == []  # User exists (no 404) but has no notifications

    # Check that only those users exists (no leakage from other tests)
    all_users_result = await db_session.exec(select(User))
    all_users_list = list(all_users_result.all())
    assert len(all_users_list) == 2
    assert all_users_list[0].id == 1
    assert all_users_list[0].email == "alice@example.com"
    assert all_users_list[1].id == 2
    assert all_users_list[1].email == "apiuser@example.com"
    # Importantly, user 3 should NOT be here, nor user 4

    # Verify only those users exists through API calls
    response = test_client.get("/api/v1/users/3/notifications")
    assert response.status_code == HTTP_404_NOT_FOUND
    response = test_client.get("/api/v1/users/4/notifications")
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
    response = test_client.post("/api/v1/registrations", json=register_data)
    assert response.status_code == HTTP_201_CREATED

    # Verify those users exists in our test database
    assert user.id is not None
    assert user.id == 1
    assert user.email == "bob@example.com"

    # Verify those users exists through API calls
    response = test_client.get(f"/api/v1/users/{user.id}/notifications")
    assert response.status_code == HTTP_200_OK
    assert response.json() == []  # User exists (no 404) but has no notifications
    response = test_client.get("/api/v1/users/2/notifications")
    assert response.status_code == HTTP_200_OK
    assert response.json() == []  # User exists (no 404) but has no notifications

    # Check that only those users exists (proving no leakage from test_one)
    all_users_result = await db_session.exec(select(User))
    all_users_list = list(all_users_result.all())
    assert len(all_users_list) == 2
    assert all_users_list[0].id == 1
    assert all_users_list[0].email == "bob@example.com"
    assert all_users_list[1].id == 2
    assert all_users_list[1].email == "apiuser2@example.com"
    # Importantly, user 3 should NOT be here, nor user 4

    # Verify only those users exists through API calls
    response = test_client.get("/api/v1/users/3/notifications")
    assert response.status_code == HTTP_404_NOT_FOUND
    response = test_client.get("/api/v1/users/4/notifications")
    assert response.status_code == HTTP_404_NOT_FOUND


async def test_do_not_register_again_when_user_and_subscription_already_exist(
    test_client: TestClient[Litestar],
    db_session: AsyncSession,
    webpushsubscription: dict[str, Any],
) -> None:
    all_registrations = await db_session.exec(select(Registration))
    assert len(all_registrations.all()) == 0

    # First registration, we're expecting a 201 CREATED.
    register_data = {"email": "foo@bar.baz", "subscription": webpushsubscription}
    response = test_client.post("/api/v1/registrations", json=register_data)
    assert response.status_code == HTTP_201_CREATED

    # Second registration, we're expecting a 200 OK, not 201 CREATED.
    register_data = {"email": "foo@bar.baz", "subscription": webpushsubscription}
    response = test_client.post("/api/v1/registrations", json=register_data)
    assert response.status_code == HTTP_200_OK  # NOT HTTP_201_CREATED.

    # Still only one registration, no duplicates.
    all_registrations = await db_session.exec(select(Registration))
    assert len(all_registrations.all()) == 1  # The registration from the fixture.


async def test_registration_default_fields(
    test_client: TestClient[Litestar],
    db_session: AsyncSession,
    webpushsubscription: dict[str, Any],
) -> None:
    all_registrations = await db_session.exec(select(Registration))
    assert len(all_registrations.all()) == 0

    # First registration, we're expecting a 201 CREATED.
    register_data = {"email": "foo@bar.baz", "subscription": webpushsubscription}
    response = test_client.post("/api/v1/registrations", json=register_data)
    assert response.status_code == HTTP_201_CREATED

    # Make sure the registration has all the default fields set properly.
    all_registrations = await db_session.exec(
        select(Registration).options(
            selectinload(cast(InstrumentedAttribute[Any], Registration.user))
        )
    )
    registration = all_registrations.one()
    assert registration.user.email == "foo@bar.baz"
    try:
        uuid.UUID(registration.label, version=4)
    except ValueError:
        pytest.fail(
            f"Label should be initialized with a uuid4, but instead is set to: '{registration.label}'"
        )
    assert registration.enabled  # By default the registration is enabled.
    assert registration.created_at < datetime.datetime.now()


async def test_registration_custom_fields(
    test_client: TestClient[Litestar],
    db_session: AsyncSession,
    webpushsubscription: dict[str, Any],
) -> None:
    all_registrations = await db_session.exec(select(Registration))
    assert len(all_registrations.all()) == 0

    # First registration, we're expecting a 201 CREATED.
    register_data = {
        "email": "foo@bar.baz",
        "label": "foobar",
        "enabled": False,
        "subscription": webpushsubscription,
    }
    response = test_client.post("/api/v1/registrations", json=register_data)
    assert response.status_code == HTTP_201_CREATED

    # Make sure the registration has all the default fields set properly.
    all_registrations = await db_session.exec(
        select(Registration).options(
            selectinload(cast(InstrumentedAttribute[Any], Registration.user))
        )
    )
    registration = all_registrations.one()
    assert registration.user.email == "foo@bar.baz"
    assert registration.label == "foobar"
    assert not registration.enabled
    assert registration.created_at < datetime.datetime.now()


async def test_list_users(
    test_client: TestClient[Litestar],
    user: User,
) -> None:
    response = test_client.get("/api/v1/users")
    assert response.status_code == HTTP_200_OK
    users = response.json()
    assert len(users) == 1
    assert users[0]["email"] == user.email


async def test_list_registrations(
    test_client: TestClient[Litestar],
    registration: Registration,
) -> None:
    response = test_client.get(f"/api/v1/users/{registration.user.id}/registrations")
    assert response.status_code == HTTP_200_OK
    registrations = response.json()
    assert len(registrations) == 1


async def test_rename_registration(
    test_client: TestClient[Litestar],
    registration: Registration,
) -> None:
    assert registration.label != "new label"
    response = test_client.patch(
        f"/api/v1/registrations/{registration.id}/label", json={"label": "new label"}
    )
    assert response.status_code == HTTP_200_OK
    registrations = response.json()
    assert registrations["label"] == "new label"


async def test_enable_registration(
    test_client: TestClient[Litestar],
    registration: Registration,
) -> None:
    # Test disabling the registration
    assert registration.enabled is True
    response = test_client.patch(
        f"/api/v1/registrations/{registration.id}/enabled", json={"enabled": False}
    )
    assert response.status_code == HTTP_200_OK
    result = response.json()
    assert result["enabled"] is False

    # Test enabling the registration
    response = test_client.patch(
        f"/api/v1/registrations/{registration.id}/enabled", json={"enabled": True}
    )
    assert response.status_code == HTTP_200_OK
    result = response.json()
    assert result["enabled"] is True


async def test_ami_fs_test_login_callback(
    test_client: TestClient[Litestar],
    httpx_mock: HTTPXMock,
    monkeypatch,  # type: ignore[reportUnknownParameterType]
) -> None:
    fake_token_json_response = {
        "access_token": "fake access token",
        "expires_in": 60,
        "id_token": "fake id token",
        "scope": "openid given_name family_name preferred_username birthdate gender birthplace birthcountry email",
        "token_type": "Bearer",
    }
    httpx_mock.add_response(
        method="POST",
        url="https://fcp-low.sbx.dev-franceconnect.fr/api/v2/token",
        json=fake_token_json_response,
    )
    httpx_mock.add_response(
        method="GET", url="https://fcp-low.sbx.dev-franceconnect.fr/api/v2/jwks"
    )
    httpx_mock.add_response(
        method="GET",
        url="https://fcp-low.sbx.dev-franceconnect.fr/api/v2/userinfo",
        json=FAKE_USERINFO,
    )

    def fake_jwt_decode(userinfo_jws: str, options: Any, algorithms: Any = ["ES256"]):
        return FAKE_USERINFO

    monkeypatch.setattr("jwt.decode", fake_jwt_decode)  # type: ignore[reportUnknownMemberType]

    response = test_client.get("/ami-fs-test-login-callback?code=fake-code")

    assert response.request.url == "http://testserver.local/"
    assert test_client.get_session_data() == {
        "id_token": "fake id token",
        "userinfo": FAKE_USERINFO,
    }


async def test_ami_fs_test_logout(
    test_client: TestClient[Litestar],
    httpx_mock: HTTPXMock,
) -> None:
    test_client.set_session_data({"id_token": "fake id token", "userinfo": FAKE_USERINFO})
    data: dict[str, str] = {
        "id_token_hint": "fake id token",
        "state": "not-implemented-yet-and-has-more-than-32-chars",
        "post_logout_redirect_uri": "https://localhost:5173/ami-fs-test-logout-callback",
    }
    params: str = urlencode(data)
    url: str = f"https://fcp-low.sbx.dev-franceconnect.fr/api/v2/session/end?{params}"

    response = test_client.get("/ami-fs-test-logout", follow_redirects=False)
    assert response.status_code == 302
    assert response.headers["location"] == url
    # Session data is still present, so if logging out from FC failed, the user can try again.
    assert test_client.get_session_data() == {
        "id_token": "fake id token",
        "userinfo": FAKE_USERINFO,
    }


async def test_ami_fs_test_logout_callback(
    test_client: TestClient[Litestar],
    httpx_mock: HTTPXMock,
) -> None:
    test_client.set_session_data({"id_token": "fake id token", "userinfo": FAKE_USERINFO})
    response = test_client.get("/ami-fs-test-logout-callback", follow_redirects=False)
    assert response.status_code == 302
    # As the user was properly logged out from FC, the local session is now emptied, and the user redirected to the app.
    assert response.headers["location"] == "/#/logged_out"
    assert test_client.get_session_data() == {}
