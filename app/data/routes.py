import asyncio
import datetime
from typing import Any

from litestar import Request, Router, get

from app.data.holidays import (
    get_holidays_dates,
    get_public_holidays_catalog,
    get_school_holidays_catalog,
)
from app.data.internal import get_elections_catalog
from app.httpx import AsyncClient
from app.schemas import Agenda


@get(path="/agenda/items", include_in_schema=False)
async def get_agenda_items(
    request: Request[Any, Any, Any],
    current_date: datetime.date,
    httpx_async_client: AsyncClient,
) -> Agenda:
    start_date, end_date = get_holidays_dates(current_date)
    agenda = Agenda()

    catalogs_mapping = {
        "school_holidays": get_school_holidays_catalog,
        "public_holidays": get_public_holidays_catalog,
        "elections": get_elections_catalog,
    }

    tasks: dict[str, asyncio.Task[Any]] = {}
    async with asyncio.TaskGroup() as task_group:
        for catalog_name, catalog_function in catalogs_mapping.items():
            tasks[catalog_name] = task_group.create_task(
                catalog_function(
                    start_date=start_date,
                    end_date=end_date,
                    httpx_async_client=httpx_async_client,
                )
            )
    for catalog_name in catalogs_mapping:
        agenda.__dict__[catalog_name] = tasks[catalog_name].result()
    return agenda


data_router: Router = Router(
    path="/data",
    route_handlers=[
        get_agenda_items,
    ],
)
