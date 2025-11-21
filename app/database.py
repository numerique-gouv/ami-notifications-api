import os
from dataclasses import dataclass

from advanced_alchemy.extensions.litestar import (
    AsyncSessionConfig,
    SQLAlchemyAsyncConfig,
    SQLAlchemyPlugin,
)
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

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


@dataclass
class DatabaseSettings:
    _engine_instance: AsyncEngine | None = None

    @property
    def engine(self) -> AsyncEngine:
        return self.get_engine()

    def get_engine(self) -> AsyncEngine:
        if self._engine_instance is not None:
            return self._engine_instance
        engine = create_async_engine(url=DATABASE_URL)

        self._engine_instance = engine
        return self._engine_instance


session_config = AsyncSessionConfig(expire_on_commit=False)
alchemy_config = SQLAlchemyAsyncConfig(
    engine_instance=DatabaseSettings().get_engine(),
    before_send_handler="autocommit_include_redirects",
    session_config=session_config,
)
alchemy = SQLAlchemyPlugin(config=alchemy_config)
