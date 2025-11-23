import datetime
from typing import Any

from litestar import Request, Response, Router, get
from litestar.security.jwt import Token

from app import env
from app.httpx import httpx
from app.models import User
from app.schemas import Holiday


@get(path="/api-particulier/quotient", include_in_schema=False)
async def get_api_particulier_quotient(
    request: Request[User, Token, Any],
) -> Response[Any]:
    """This endpoint "forwards" the request coming from the frontend (the app).

    API Particulier doesn't implement CORS, so the app can't directly query it.
    We thus have this endpoint to act as some kind of proxy.

    """
    response = httpx.get(
        f"{env.PUBLIC_API_PARTICULIER_BASE_URL}{env.PUBLIC_API_PARTICULIER_QUOTIENT_ENDPOINT}?recipient={env.PUBLIC_API_PARTICULIER_RECIPIENT_ID}",
        headers={"authorization": request.headers["fc_authorization"]},
    )
    return Response(response.content, status_code=response.status_code)


@get(path="/holidays", include_in_schema=False)
async def get_holidays(
    request: Request[Any, Any, Any],
    current_date: datetime.date,
) -> list[Holiday]:
    # target one region per zone, to limit results
    locations = ["Bordeaux", "Lille", "Versailles"]
    locations_query = " OR ".join(f"location = '{location}'" for location in locations)

    # if the school year that has just begun, take holidays until the end of the current school year
    # else, take the holidays until the end of the following school year
    end_date = f"{current_date.year + 1}-09-15"

    response = httpx.get(
        f"{env.PUBLIC_API_DATA_EDUCATION_BASE_URL}{env.PUBLIC_API_DATA_EDUCATION_HOLIDAYS_ENDPOINT}",
        params={
            "where": f"end_date >= date'{current_date}' AND start_date < date'{end_date}' AND ({locations_query}) AND population IN ('-', 'Élèves')",
            "order_by": "start_date",
            "limit": 100,
        },
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
