from collections.abc import AsyncGenerator, Iterator
from contextlib import asynccontextmanager

import pytest
from litestar import Litestar
from litestar.testing import TestClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession
from webpush import WebPush
from webpush.vapid import VAPID

from app import Notification, Registration, create_app
from app.database import DATABASE_URL


@pytest.fixture
async def app():
    app_ = create_app(database_connection=test_db_connection, webpush_init=test_webpush)
    app_.debug = True
    return app_


@asynccontextmanager
async def test_db_connection(app: Litestar) -> AsyncGenerator[None, None]:
    engine = getattr(app.state, "engine", None)
    if engine is None:
        engine = create_async_engine(DATABASE_URL)
        app.state.engine = engine
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    try:
        yield
    finally:
        async with engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.drop_all)
        await engine.dispose()


def test_webpush() -> WebPush:
    private_key, public_key, _ = VAPID.generate_keys()

    return WebPush(
        private_key=private_key,
        public_key=public_key,
        subscriber="administrator@example.com",
    )


@pytest.fixture
def test_client(app) -> Iterator[TestClient[Litestar]]:
    with TestClient(app=app) as client:
        yield client


@pytest.fixture
async def db_session(app) -> AsyncGenerator[AsyncSession, None]:
    sessionmaker = async_sessionmaker(class_=AsyncSession, expire_on_commit=False)

    async with sessionmaker(bind=app.state.engine) as session:
        yield session


@pytest.fixture
async def notification(db_session, registration) -> Notification:
    notification = Notification(
        email=registration.email,
        message="Hello notification",
        title="Notification title",
        sender="John Doe",
    )
    db_session.add(notification)
    await db_session.commit()
    return notification


@pytest.fixture
async def registration(db_session, webpushsubscription) -> Registration:
    registration_ = Registration(email="user@example.com", subscription=webpushsubscription)
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
