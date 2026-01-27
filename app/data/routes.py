import datetime
from typing import Any

from litestar import Request, Response, Router, get

from app.data.holidays import (
    SchoolHolidaysError,
    get_holidays_dates,
    get_public_holidays_data,
    get_school_holidays_data,
)
from app.httpx import AsyncClient
from app.schemas import PublicHoliday, SchoolHoliday
from app.utils import error_from_message


@get(path="/school-holidays", include_in_schema=False)
async def get_school_holidays(
    request: Request[Any, Any, Any],
    current_date: datetime.date,
    httpx_async_client: AsyncClient,
) -> list[SchoolHoliday] | Response[dict[Any, Any]]:
    start_date, end_date = get_holidays_dates(current_date)
    try:
        result = await get_school_holidays_data(start_date, end_date, httpx_async_client)
        return result
    except SchoolHolidaysError as e:
        return error_from_message(
            {"ami_details": "School holidays error"}, status_code=e.status_code
        )


@get(path="/public-holidays", include_in_schema=False)
def get_public_holidays(
    request: Request[Any, Any, Any],
    current_date: datetime.date,
) -> list[PublicHoliday]:
    start_date, end_date = get_holidays_dates(current_date)
    return get_public_holidays_data(start_date, end_date)


data_router: Router = Router(
    path="/data",
    route_handlers=[
        get_school_holidays,
        get_public_holidays,
    ],
)
