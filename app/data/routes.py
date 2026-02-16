import asyncio
import datetime
from typing import Annotated, Any

from advanced_alchemy.extensions.litestar import providers
from litestar import Request, Router, get
from litestar.di import Provide
from litestar.params import Parameter

from app.data.holidays import (
    get_holidays_dates,
    get_public_holidays_catalog,
    get_school_holidays_catalog,
)
from app.data.internal import get_elections_catalog
from app.data.partners import get_psl_inventory
from app.data.schemas import (
    Agenda,
    AgendaCatalogStatus,
    DurationExpiration,
    FollowUp,
    MonthlyExpiration,
    TimeUnit,
)
from app.httpx import AsyncClient
from app.models import User
from app.services.notification import NotificationService
from app.services.user import provide_user

CATALOG_EXPIRATION_RULES = {
    "school_holidays": MonthlyExpiration(),
    "public_holidays": MonthlyExpiration(),
    "elections": DurationExpiration(amount=1, unit=TimeUnit.DAYS),
}


@get(path="/agenda/items", include_in_schema=False)
async def get_agenda_items(
    request: Request[Any, Any, Any],
    current_date: datetime.date,
    filter_items: Annotated[list[str] | None, Parameter(query="filter-items")],
    httpx_async_client: AsyncClient,
) -> Agenda:
    start_date, end_date = get_holidays_dates(current_date)
    agenda = Agenda()

    catalogs_mapping = {
        "school_holidays": get_school_holidays_catalog,
        "public_holidays": get_public_holidays_catalog,
        "elections": get_elections_catalog,
    }

    item_keys = filter_items or []
    item_keys = [f for f in item_keys if f in catalogs_mapping] or catalogs_mapping.keys()

    tasks: dict[str, asyncio.Task[Any]] = {}
    async with asyncio.TaskGroup() as task_group:
        for catalog_name in item_keys:
            tasks[catalog_name] = task_group.create_task(
                catalogs_mapping[catalog_name](
                    start_date=start_date,
                    end_date=end_date,
                    httpx_async_client=httpx_async_client,
                )
            )
    for catalog_name in catalogs_mapping:
        if catalog_name not in item_keys:
            agenda.__dict__[catalog_name] = None
            continue
        result = tasks[catalog_name].result()
        if result.status == AgendaCatalogStatus.SUCCESS:
            result.set_expires_at(CATALOG_EXPIRATION_RULES[catalog_name])
        agenda.__dict__[catalog_name] = result
    return agenda


@get(
    path="/follow-up/inventories",
    include_in_schema=False,
    dependencies={
        "notifications_service": providers.create_service_provider(NotificationService),
        "current_user": Provide(provide_user),
    },
)
async def get_follow_up_inventories(
    request: Request[Any, Any, Any],
    current_user: User,
    notifications_service: NotificationService,
) -> FollowUp:
    follow_up = FollowUp()

    follow_up.psl = await get_psl_inventory(
        current_user=current_user,
        notifications_service=notifications_service,
    )

    return follow_up


data_router: Router = Router(
    path="/data",
    route_handlers=[
        get_agenda_items,
        get_follow_up_inventories,
    ],
)
