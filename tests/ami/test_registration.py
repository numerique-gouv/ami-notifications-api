import datetime
import uuid
from typing import Any

from litestar import Litestar
from litestar.status_codes import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_204_NO_CONTENT,
    HTTP_404_NOT_FOUND,
)
from litestar.testing import TestClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Registration, User
from tests.ami.utils import assert_query_fails_without_auth, login


async def test_register(
    test_client: TestClient[Litestar],
    db_session: AsyncSession,
    user: User,
    webpushsubscription: dict[str, Any],
) -> None:
    login(user, test_client)

    all_registrations = await db_session.execute(select(Registration))
    assert len(all_registrations.scalars().all()) == 0

    # First registration, we're expecting a 201 CREATED.
    register_data = {
        "subscription": webpushsubscription,
    }
    response = test_client.post("/api/v1/users/registrations", json=register_data)
    assert response.status_code == HTTP_201_CREATED

    all_registrations = (await db_session.execute(select(Registration))).scalars().all()
    assert len(all_registrations) == 1
    registration = all_registrations[0]
    registration_id = registration.id

    # Second registration, we're expecting a 200 OK, not 201 CREATED.
    register_data = {
        "subscription": webpushsubscription,
    }
    response = test_client.post("/api/v1/users/registrations", json=register_data)
    assert response.status_code == HTTP_200_OK

    all_registrations = (await db_session.execute(select(Registration))).scalars().all()
    assert len(all_registrations) == 1
    registration = all_registrations[0]
    assert registration.id == registration_id


async def test_register_fields(
    test_client: TestClient[Litestar],
    db_session: AsyncSession,
    user: User,
    webpushsubscription: dict[str, Any],
) -> None:
    login(user, test_client)

    # id, created_at and updated_at are ignored
    registration_date: datetime.datetime = datetime.datetime.now(
        datetime.timezone.utc
    ) + datetime.timedelta(days=1)
    registration_id: uuid.UUID = uuid.uuid4()
    registration_data = {
        "subscription": webpushsubscription,
        "id": str(registration_id),
        "created_at": registration_date.isoformat(),
        "updated_at": registration_date.isoformat(),
    }
    response = test_client.post("/api/v1/users/registrations", json=registration_data)
    assert response.status_code == HTTP_201_CREATED

    all_registrations = (await db_session.execute(select(Registration))).scalars().all()
    assert len(all_registrations) == 1
    registration = all_registrations[0]
    assert registration.id != registration_id
    assert registration.created_at < registration_date
    assert registration.updated_at < registration_date


async def test_register_without_auth(
    test_client: TestClient[Litestar],
) -> None:
    await assert_query_fails_without_auth("/api/v1/users/registrations", test_client, method="post")


async def test_unregister(
    test_client: TestClient[Litestar],
    db_session: AsyncSession,
    registration: Registration,
) -> None:
    login(registration.user, test_client)

    all_registrations = (await db_session.execute(select(Registration))).scalars().all()
    assert len(all_registrations) == 1

    response = test_client.delete(f"/api/v1/users/registrations/{registration.id}")
    assert response.status_code == HTTP_204_NO_CONTENT

    all_registrations = (await db_session.execute(select(Registration))).scalars().all()
    assert len(all_registrations) == 0

    # registration does not exist
    response = test_client.delete(f"/api/v1/users/registrations/{registration.id}")
    assert response.status_code == HTTP_404_NOT_FOUND

    # registration of another user than current user
    other_user = User(fc_hash="fc-hash")
    db_session.add(other_user)
    await db_session.commit()
    other_registration = Registration(
        user_id=other_user.id,
    )
    db_session.add(other_registration)
    await db_session.commit()
    response = test_client.delete(f"/api/v1/users/registrations/{registration.id}")
    assert response.status_code == HTTP_404_NOT_FOUND


async def test_unregister_without_auth(
    test_client: TestClient[Litestar],
    registration: Registration,
) -> None:
    await assert_query_fails_without_auth(
        f"/api/v1/users/registrations/{registration.id}", test_client, method="delete"
    )


async def test_list_registrations(
    test_client: TestClient[Litestar],
    registration: Registration,
) -> None:
    login(registration.user, test_client)

    response = test_client.get("/api/v1/users/registrations")
    assert response.status_code == HTTP_200_OK
    registrations = response.json()
    assert len(registrations) == 1
    assert set(response.json()[0].keys()) == {"id", "user_id", "subscription", "created_at"}
    assert response.json()[0]["id"] == str(registration.id)
    assert response.json()[0]["user_id"] == str(registration.user_id)
    assert response.json()[0]["subscription"] == registration.subscription
    assert response.json()[0]["created_at"] == registration.created_at.isoformat().replace(
        "+00:00", "Z"
    )


async def test_list_registrations_without_auth(
    test_client: TestClient[Litestar],
) -> None:
    await assert_query_fails_without_auth("/api/v1/users/registrations", test_client)
