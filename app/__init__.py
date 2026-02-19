from pathlib import Path
from typing import Any

import firebase_admin
import sentry_sdk
from litestar import (
    Litestar,
    Response,
    Router,
    get,
    head,
)
from litestar.channels import ChannelsPlugin
from litestar.channels.backends.asyncpg import AsyncPgChannelsBackend
from litestar.config.cors import CORSConfig
from litestar.contrib.jinja import JinjaTemplateEngine
from litestar.di import Provide
from litestar.static_files import (
    create_static_files_router,  # type: ignore[reportUnknownVariableType]
)
from litestar.stores.file import FileStore
from litestar.template.config import TemplateConfig
from sentry_sdk.integrations.litestar import LitestarIntegration
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine

from app import env, errors
from app.auth import jwt_cookie_auth, openapi_config, partner_auth
from app.cli import CLIPlugin
from app.controllers.auth import AuthController
from app.controllers.notification import (
    NotAuthenticatedNotificationController,
    NotificationController,
    PartnerNotificationController,
)
from app.controllers.partner import NotAuthenticatedPartnerController, PartnerController
from app.controllers.registration import RegistrationController
from app.controllers.scheduled_notification import ScheduledNotificationController
from app.database import alchemy, alchemy_config, channels_dsn
from app.httpx import (
    AsyncClient,
    close_httpx_async_client,
    get_httpx_async_client,
    httpx_async_client_provider,
)
from app.utils import build_fc_hash
from app.webpush import provide_webpush

from .admin.routes import router as ami_admin_router
from .data.routes import data_router
from .rvo.routes import router as rvo_router

cors_config = CORSConfig(allow_origins=[env.PUBLIC_APP_URL], allow_credentials=True)
firebase_app: firebase_admin.App = firebase_admin.initialize_app()  # type: ignore[reportUnknownMemberType]


sentry_sdk.init(
    dsn=env.SENTRY_DSN,
    environment=env.SENTRY_ENV,
    # Add data like request headers and IP for users, if applicable;
    # see https://docs.sentry.io/platforms/python/data-management/data-collected/ for more info
    # send_default_pii=True,
    integrations=[
        LitestarIntegration(
            failed_request_status_codes={s for s in range(400, 599) if s != 401},
        ),
    ],
)

# ### VIEWS


@head(path="/ping", include_in_schema=False)
async def ping() -> None:
    pass


@get(path="/sector_identifier_url", include_in_schema=False)
async def get_sector_identifier_url() -> Response[Any]:
    redirect_uris: list[str] = [
        url.strip() for url in env.PUBLIC_SECTOR_IDENTIFIER_URL.strip().split("\n")
    ]
    return Response(redirect_uris)


# ### DEV ENDPOINTS


@get(path="/dev-utils/recipient-fc-hash")
async def _dev_utils_recipient_fc_hash(
    given_name: str,
    family_name: str,
    birthdate: str,
    gender: str,
    birthplace: str | None,
    birthcountry: str,
) -> str:
    birthplace = birthplace or ""
    hashed_pivot_data: str = build_fc_hash(
        given_name=given_name,
        family_name=family_name,
        birthdate=birthdate,
        gender=gender,
        birthplace=birthplace,
        birthcountry=birthcountry,
    )
    return hashed_pivot_data


@get(path="/dev-utils/review-apps")
async def _dev_utils_review_apps(httpx_async_client: AsyncClient) -> list[dict[str, str | int]]:
    """Returns a list of tuples: (review app url, pull request title)."""
    response = await httpx_async_client.get(
        "https://api.github.com/repos/numerique-gouv/ami-notifications-api/pulls",
        params={"state": "open", "sort": "created", "per_page": 100},
        headers={
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    staging_app = {
        "url": "https://ami-back-staging.osc-fr1.scalingo.io/",
        "title": "Staging",
        "number": 0,
        "description": "Staging",
    }
    if response.status_code >= 400:
        # Possibly rate limited
        return [staging_app]

    json_data = response.json()
    review_apps = [
        {
            "url": f"https://ami-back-staging-pr{review_app['number']}.osc-fr1.scalingo.io/",
            "title": f"PR{review_app['number']}: {review_app['title']}",
            "number": review_app["number"],
            "description": review_app["body"],
        }
        for review_app in json_data
    ]
    return [staging_app] + review_apps


@get(path="/dev-utils/health/db-pool")
async def _dev_health_db_pool(db_engine: AsyncEngine) -> Any:
    """Returns database connection pool statistics for monitoring."""
    engine = alchemy_config.get_engine()
    async with engine.connect() as conn:
        result = await conn.execute(
            text("""
          SELECT
              pid,
              usename,
              application_name,
              client_addr,
              state,
              query,
              EXTRACT(EPOCH FROM (now() - state_change)) as duration_seconds
          FROM pg_stat_activity
          WHERE datname = current_database()
          AND pid != pg_backend_pid()
          ORDER BY state_change
      """)
        )
    return {
        "status": db_engine.pool.status(),
        "connections": [row._asdict() for row in result.fetchall()],  # type: ignore[reportPrivateUsage]
    }


# ### APP


authenticated_router: Router = Router(
    path="/",
    route_handlers=[
        AuthController,
        RegistrationController,
        NotificationController,
        PartnerController,
        ScheduledNotificationController,
        data_router,
    ],
    middleware=[jwt_cookie_auth.middleware],
)

partner_router: Router = Router(
    path="/",
    route_handlers=[PartnerNotificationController],
    middleware=[partner_auth.middleware],
)


def create_app() -> Litestar:
    return Litestar(
        route_handlers=[
            authenticated_router,
            partner_router,
            NotAuthenticatedNotificationController,
            NotAuthenticatedPartnerController,
            ping,
            get_sector_identifier_url,
            _dev_utils_recipient_fc_hash,
            _dev_utils_review_apps,
            _dev_health_db_pool,
            create_static_files_router(
                path="/",
                directories=[env.HTML_DIR],
                html_mode=True,
            ),
            rvo_router,
            ami_admin_router,
        ],
        exception_handlers={errors.TechnicalError: errors.technical_error_handler},
        dependencies={
            "webpush": Provide(provide_webpush, use_cache=True, sync_to_thread=True),
            "httpx_async_client": Provide(httpx_async_client_provider),
        },
        plugins=[
            alchemy,
            ChannelsPlugin(
                channels=["notification_events"], backend=AsyncPgChannelsBackend(dsn=channels_dsn)
            ),
            CLIPlugin(),
        ],
        template_config=TemplateConfig(directory=Path("templates"), engine=JinjaTemplateEngine),
        cors_config=cors_config,
        stores={"sessions": FileStore(path=Path("session_data"))},
        openapi_config=openapi_config,
        on_startup=[get_httpx_async_client],
        on_shutdown=[close_httpx_async_client],
    )
