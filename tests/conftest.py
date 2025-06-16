from collections.abc import AsyncGenerator, Iterator
from contextlib import asynccontextmanager

import pytest
from litestar import Litestar
from litestar.testing import TestClient
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, create_async_engine
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession
from webpush import WebPush
from webpush.vapid import VAPID

from app import Notification, Registration, User, create_app
from app.database import DATABASE_URL

TEST_DATABASE_URL = f"{DATABASE_URL}_test"


def test_webpush() -> WebPush:
    """Create a test WebPush instance with generated keys."""
    private_key, public_key, _ = VAPID.generate_keys()
    return WebPush(
        private_key=private_key,
        public_key=public_key,
        subscriber="administrator@example.com",
    )


@asynccontextmanager
async def test_db_connection(app: Litestar) -> AsyncGenerator[None, None]:
    """Database connection for the app."""
    engine = create_async_engine(TEST_DATABASE_URL)
    app.state.engine = engine

    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    try:
        yield
    finally:
        async with engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.drop_all)
        await engine.dispose()


@pytest.fixture
async def app():
    """Create app with test database connection."""
    app_ = create_app(database_connection=test_db_connection, webpush_init=test_webpush)
    app_.debug = True
    return app_


@pytest.fixture
def test_client(app) -> Iterator[TestClient[Litestar]]:
    """Create a sync test client for the app."""
    with TestClient(app=app) as client:
        yield client


@pytest.fixture
async def test_engine() -> AsyncGenerator[AsyncEngine, None]:
    """Create a fresh database engine for each test with proper cleanup."""
    engine = create_async_engine(TEST_DATABASE_URL)

    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    try:
        yield engine
    finally:
        # Clean up - drop tables and dispose engine
        async with engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.drop_all)
        await engine.dispose()


@pytest.fixture
async def db_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create a database session using the test engine."""
    sessionmaker = async_sessionmaker(bind=test_engine, class_=AsyncSession, expire_on_commit=False)
    async with sessionmaker() as session:
        yield session


@pytest.fixture
async def user(db_session) -> User:
    user_ = User(email="user@example.com")
    db_session.add(user_)
    await db_session.commit()
    return user_


@pytest.fixture
async def notification(db_session, registration) -> Notification:
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
async def registration(db_session, user, webpushsubscription) -> Registration:
    registration_ = Registration(user_id=user.id, subscription=webpushsubscription)
    db_session.add(registration_)
    await db_session.commit()
    return registration_


@pytest.fixture
async def webpushsubscription() -> dict:
    subscription = {
        "endpoint": "https://example.com",
        "keys": {
            "auth": "ribfIxhEOtCZ0lkcbB4yCg",
            "p256dh": "BGsTJAJDhGijvPLi0DVPHB86MGLmW1Y6VzjX-FpTlKbhhOtCmU0Vffaj1djCXzR6vkUYrwkOTmh1dgbIQHEyy1k",
        },
    }
    return subscription
