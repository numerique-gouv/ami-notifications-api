import datetime
from typing import Any, Iterable, cast

from workalendar.europe import France

from app import env
from app.httpx import AsyncClient
from app.schemas import PublicHoliday, SchoolHoliday


class SchoolHolidaysError(Exception):
    def __init__(self, status_code: int, *args: Any, **kwargs: Any):
        self.status_code = status_code
        super().__init__(*args, **kwargs)


def get_holidays_dates(current_date: datetime.date) -> tuple[datetime.date, datetime.date]:
    # take holidays from the previous month:
    # if current_date falls during a holiday with zone, then we will be sure to retrieve all zones,
    # and we will always be able to deduplicate correctly
    start_date = current_date - datetime.timedelta(days=30)
    # if the school year has just begun, take holidays until the end of the current school year
    # else, take holidays until the end of the following school year
    end_date = datetime.date(current_date.year + 1, 9, 15)
    return start_date, end_date


async def get_school_holidays_data(
    start_date: datetime.date,
    end_date: datetime.date,
    httpx_async_client: AsyncClient,
) -> list[SchoolHoliday]:
    # target one region per zone, to limit results
    locations = ["Bordeaux", "Lille", "Versailles"]
    locations_query = " OR ".join(f"location = '{location}'" for location in locations)

    response = await httpx_async_client.get(
        f"{env.PUBLIC_API_DATA_EDUCATION_BASE_URL}{env.PUBLIC_API_DATA_EDUCATION_HOLIDAYS_ENDPOINT}",
        params={
            "where": f"end_date >= date'{start_date}' AND start_date < date'{end_date}' AND ({locations_query}) AND population IN ('-', 'Élèves')",
            "order_by": "start_date",
            "limit": 100,
        },
    )
    if response.status_code != 200:
        raise SchoolHolidaysError(status_code=response.status_code)

    holidays: dict[Any, SchoolHoliday] = {}
    for data in response.json()["results"]:
        holiday = SchoolHoliday.from_dict(data)
        key = (holiday.description, holiday.start_date, holiday.end_date)
        if key in holidays:
            # if the dates are the same for all zones, keep only one result and clear zones
            holidays[key].zones = ""
            continue
        holidays[key] = holiday

    return sorted(holidays.values(), key=lambda a: a.start_date)


def get_public_holidays_data(
    start_date: datetime.date,
    end_date: datetime.date,
) -> list[PublicHoliday]:
    calendar = France()

    workalendar_holidays: list[tuple[datetime.date, str]] = [
        day
        for year in range(start_date.year, end_date.year + 1)
        for day in cast(
            Iterable[tuple[datetime.date, str]],
            calendar.holidays(year),  # type: ignore
        )
    ]

    holidays: list[PublicHoliday] = []
    for day, description in workalendar_holidays:
        if day < start_date or day > end_date:
            continue
        holidays.append(PublicHoliday.from_dict({"description": description, "date": day}))
    return holidays
