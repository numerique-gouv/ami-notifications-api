import os

from advanced_alchemy.extensions.litestar import (
    AsyncSessionConfig,
    EngineConfig,
    SQLAlchemyAsyncConfig,
    SQLAlchemyPlugin,
)

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


session_config = AsyncSessionConfig(expire_on_commit=False)
alchemy_config = SQLAlchemyAsyncConfig(
    connection_string=DATABASE_URL,
    engine_config=EngineConfig(pool_pre_ping=True),
    session_config=session_config,
    before_send_handler="autocommit_include_redirects",
)
alchemy = SQLAlchemyPlugin(config=alchemy_config)
