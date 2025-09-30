from collections.abc import AsyncGenerator, Iterator
from contextlib import asynccontextmanager
from typing import Any

import pytest
from litestar import Litestar
from litestar.testing import TestClient
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, create_async_engine
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession
from webpush import WebPush
from webpush.vapid import VAPID

from app import Notification, Registration, User, create_app, session_config
from app.database import DATABASE_URL

TEST_DATABASE_URL = f"{DATABASE_URL}_test"


@asynccontextmanager
async def yield_engine() -> AsyncGenerator[AsyncEngine, None]:
    engine = create_async_engine(TEST_DATABASE_URL)

    # Make sure the database is empty when we start.
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)

    # Create all tables.
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    try:
        yield engine
    finally:
        # Clean up - drop tables and dispose engine.
        async with engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.drop_all)
        await engine.dispose()


@asynccontextmanager
async def test_db_connection(app: Litestar) -> AsyncGenerator[None, None]:
    """Database connection for the app's lifespan."""
    async with yield_engine() as engine:
        app.state.engine = engine
        yield


def test_webpush() -> WebPush:
    private_key, public_key, _ = VAPID.generate_keys()
    return WebPush(
        private_key=private_key,
        public_key=public_key,
        subscriber="administrator@example.com",
    )


@pytest.fixture
async def app() -> Litestar:
    """Create app with test database connection."""
    app_ = create_app(database_connection=test_db_connection, webpush_init=test_webpush)
    app_.debug = True
    return app_


@pytest.fixture
def test_client(app: Litestar) -> Iterator[TestClient[Litestar]]:
    with TestClient(app=app, session_config=session_config) as client:
        yield client


@pytest.fixture
async def test_engine() -> AsyncGenerator[AsyncEngine, None]:
    """Create a fresh database engine for each test with proper cleanup.

    This is a duplication of the `test_db_connection` to avoid some bug around event loops:

    https://github.com/litestar-org/litestar/issues/1920#issuecomment-2592572498

    So we create an engine to be used by the `db_session` fixture, created in the context/scope
    of the tests event loop, instead of using the `app.state.engine`.

    """
    async with yield_engine() as engine:
        yield engine


@pytest.fixture
async def db_session(
    test_engine: AsyncEngine,
) -> AsyncGenerator[AsyncSession, None]:
    """Create a database session using the test engine."""
    sessionmaker = async_sessionmaker(bind=test_engine, class_=AsyncSession, expire_on_commit=False)
    async with sessionmaker() as session:
        yield session


@pytest.fixture
async def user(db_session: AsyncSession) -> User:
    user_ = User(email="user@example.com")
    db_session.add(user_)
    await db_session.commit()
    return user_


@pytest.fixture
async def notification(db_session: AsyncSession, registration: Registration) -> Notification:
    assert registration.user.id is not None, "Registration user ID should be set"
    notification_ = Notification(
        user_id=registration.user.id,
        message="Hello notification",
        title="Notification title",
        sender="John Doe",
    )
    db_session.add(notification_)
    await db_session.commit()
    return notification_


@pytest.fixture
async def registration(
    db_session: AsyncSession, user: User, webpushsubscription: dict[str, Any]
) -> Registration:
    assert user.id is not None, "User ID should be set"
    registration_ = Registration(user_id=user.id, subscription=webpushsubscription)
    db_session.add(registration_)
    await db_session.commit()
    return registration_


@pytest.fixture
async def webpushsubscription() -> dict[str, Any]:
    subscription = {
        "endpoint": "https://example.com",
        "keys": {
            "auth": "ribfIxhEOtCZ0lkcbB4yCg",
            "p256dh": "BGsTJAJDhGijvPLi0DVPHB86MGLmW1Y6VzjX-FpTlKbhhOtCmU0Vffaj1djCXzR6vkUYrwkOTmh1dgbIQHEyy1k",
        },
    }
    return subscription


@pytest.fixture
async def userinfo() -> dict[str, Any]:
    return {
        "sub": "fake sub",
        "given_name": "Angela Claire Louise",
        "given_name_array": ["Angela", "Claire", "Louise"],
        "family_name": "DUBOIS",
        "birthdate": "1962-08-24",
        "birthcountry": "99100",
        "birthplace": "75107",
        "gender": "female",
        "email": "angela@dubois.fr",
        "aud": "fake aud",
        "exp": 1753877658,
        "iat": 1753877598,
        "iss": "https://fcp-low.sbx.dev-franceconnect.fr/api/v2",
    }
