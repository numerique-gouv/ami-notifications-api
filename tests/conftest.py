from collections.abc import AsyncGenerator, Iterator
from contextlib import asynccontextmanager

import pytest
from litestar import Litestar
from litestar.testing import TestClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

from app import Notification, create_app
from app.database import DATABASE_URL


@pytest.fixture
async def app():
    app_ = create_app(database_connection=test_db_connection)
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
async def notification1(app, db_session) -> Notification:
    notification_1 = Notification(email="foo@example.com", message="Hello notification 1")
    db_session.add(notification_1)
    await db_session.commit()
    return notification_1
