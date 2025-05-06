import os
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from litestar import Litestar
from litestar.datastructures import State
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

DATABASE_URL_RAW = os.getenv("DATABASE_URL", "")
# If we get a url with extra options like ?sslmode=prefer or not using the
# propper protocol `postgresql+asyncpg`, fix it.
DATABASE_URL = (
    DATABASE_URL_RAW.replace(
        # SqlAlchemy has deprecated the use of `postgres` in favor of `postgresql`: https://github.com/sqlalchemy/sqlalchemy/issues/6083#issuecomment-801478013
        "postgres://",
        "postgresql://",
    )
    .replace(
        # We use litestar which is an async web framework, but scalingo auto configures a connection string with `postgres://"
        "postgresql://",
        "postgresql+asyncpg://",
    )
    .replace(
        # ssl mode doesn't seem to play well with SqlAlchemy.
        "?sslmode=prefer",
        "",
    )
)


@asynccontextmanager
async def db_connection(app: Litestar) -> AsyncGenerator[None, None]:
    engine = getattr(app.state, "engine", None)
    if engine is None:
        engine = create_async_engine(DATABASE_URL)
        app.state.engine = engine
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    try:
        yield
    finally:
        await engine.dispose()


sessionmaker = async_sessionmaker(class_=AsyncSession, expire_on_commit=False)


async def provide_db_session(state: State) -> AsyncGenerator[AsyncSession, None]:
    async with sessionmaker(bind=state.engine) as session:
        yield session
