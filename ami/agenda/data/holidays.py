import datetime


def get_holidays_dates(current_date: datetime.date) -> tuple[datetime.date, datetime.date]:
    # take holidays from the previous month:
    # if current_date falls during a holiday with zone, then we will be sure to retrieve all zones,
    # and we will always be able to deduplicate correctly
    start_date = current_date - datetime.timedelta(days=30)
    # if the school year has just begun, take holidays until the end of the current school year
    # else, take holidays until the end of the following school year
    end_date = datetime.date(current_date.year + 1, 9, 15)
    return start_date, end_date
