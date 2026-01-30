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

    task_school_holidays = None
    task_public_holidays = None
    task_elections = None
    async with asyncio.TaskGroup() as task_group:
        task_school_holidays = task_group.create_task(
            get_school_holidays_catalog(start_date, end_date, httpx_async_client)
        )
        task_public_holidays = task_group.create_task(
            get_public_holidays_catalog(start_date, end_date)
        )
        task_elections = task_group.create_task(get_elections_catalog(start_date, end_date))
    agenda.school_holidays = task_school_holidays.result()
    agenda.public_holidays = task_public_holidays.result()
    agenda.elections = task_elections.result()
    return agenda


data_router: Router = Router(
    path="/data",
    route_handlers=[
        get_agenda_items,
    ],
)
