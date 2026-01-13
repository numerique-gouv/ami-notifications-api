import datetime
from typing import Any

from litestar import Request, Response, Router, get
from litestar.security.jwt import Token

from app import env
from app.httpx import httpx
from app.models import User
from app.schemas import Holiday
from app.utils import error_from_message


@get(path="/api-particulier/quotient", include_in_schema=False)
async def get_api_particulier_quotient(
    request: Request[User, Token, Any],
) -> Response[Any]:
    """This endpoint "forwards" the request coming from the frontend (the app).

    API Particulier doesn't implement CORS, so the app can't directly query it.
    We thus have this endpoint to act as some kind of proxy.

    """
    if "cnaf_quotient_familial" not in env.PUBLIC_FC_SCOPE:
        # For now, in production, FC isn't qualified for the "quotient familial" scope, so don't even request it.
        return Response(None, status_code=204)
    response = httpx.get(
        f"{env.PUBLIC_API_PARTICULIER_BASE_URL}{env.PUBLIC_API_PARTICULIER_QUOTIENT_ENDPOINT}?recipient={env.PUBLIC_API_PARTICULIER_RECIPIENT_ID}",
        headers={"authorization": request.headers["fc_authorization"]},
    )
    return Response(response.content, status_code=response.status_code)


@get(path="/holidays", include_in_schema=False)
async def get_holidays(
    request: Request[Any, Any, Any],
    current_date: datetime.date,
) -> list[Holiday] | Response[dict[Any, Any]]:
    # target one region per zone, to limit results
    locations = ["Bordeaux", "Lille", "Versailles"]
    locations_query = " OR ".join(f"location = '{location}'" for location in locations)

    # take holidays from the previous month:
    # if current_date falls during a holiday with zone, then we will be sure to retrieve all zones,
    # and we will always be able to deduplicate correctly
    start_date = current_date - datetime.timedelta(days=30)
    # if the school year has just begun, take holidays until the end of the current school year
    # else, take holidays until the end of the following school year
    end_date = f"{current_date.year + 1}-09-15"

    response = httpx.get(
        f"{env.PUBLIC_API_DATA_EDUCATION_BASE_URL}{env.PUBLIC_API_DATA_EDUCATION_HOLIDAYS_ENDPOINT}",
        params={
            "where": f"end_date >= date'{start_date}' AND start_date < date'{end_date}' AND ({locations_query}) AND population IN ('-', 'Élèves')",
            "order_by": "start_date",
            "limit": 100,
        },
    )
    if response.status_code != 200:
        return error_from_message(
            {"ami_details": "Holidays error"}, status_code=response.status_code
        )

    holidays: dict[Any, Holiday] = {}
    for data in response.json()["results"]:
        holiday = Holiday.from_dict(data)
        key = (holiday.description, holiday.start_date, holiday.end_date)
        if key in holidays:
            # if the dates are the same for all zones, keep only one result and clear zones
            holidays[key].zones = ""
            continue
        holidays[key] = holiday

    return sorted(holidays.values(), key=lambda a: a.start_date)


data_router: Router = Router(
    path="/data",
    route_handlers=[
        get_api_particulier_quotient,
        get_holidays,
    ],
)
