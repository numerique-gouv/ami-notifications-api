import datetime

from app.data.holidays import get_holidays_dates


async def test_get_holidays_dates() -> None:
    # get holidays of current school year only
    assert get_holidays_dates(datetime.date(2025, 9, 1)) == (
        datetime.date(2025, 8, 2),
        datetime.date(2026, 9, 15),
    )
    assert get_holidays_dates(datetime.date(2025, 12, 31)) == (
        datetime.date(2025, 12, 1),
        datetime.date(2026, 9, 15),
    )

    # get holidays of current and next school years
    assert get_holidays_dates(datetime.date(2026, 1, 1)) == (
        datetime.date(2025, 12, 2),
        datetime.date(2027, 9, 15),
    )
    assert get_holidays_dates(datetime.date(2026, 8, 1)) == (
        datetime.date(2026, 7, 2),
        datetime.date(2027, 9, 15),
    )
