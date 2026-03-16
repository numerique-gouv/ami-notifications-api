import datetime
from typing import Any, Iterable, cast

from workalendar.europe import France

from ami.agenda.data.schemas import PublicHoliday
from ami.agenda.schemas import AgendaCatalog, AgendaCatalogStatus


def get_holidays_dates(current_date: datetime.date) -> tuple[datetime.date, datetime.date]:
    # take holidays from the previous month:
    # if current_date falls during a holiday with zone, then we will be sure to retrieve all zones,
    # and we will always be able to deduplicate correctly
    start_date = current_date - datetime.timedelta(days=30)
    # if the school year has just begun, take holidays until the end of the current school year
    # else, take holidays until the end of the following school year
    end_date = datetime.date(current_date.year + 1, 9, 15)
    return start_date, end_date


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


def get_public_holidays_catalog(
    *,
    start_date: datetime.date,
    end_date: datetime.date,
    **kwargs: Any,
) -> AgendaCatalog:
    holidays = get_public_holidays_data(start_date, end_date)
    catalog = AgendaCatalog()
    for holiday in holidays:
        catalog.items.append(holiday.to_catalog_item())
    catalog.status = AgendaCatalogStatus.SUCCESS
    return catalog
