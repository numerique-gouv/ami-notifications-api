from typing import Any

import httpx
from litestar import Request, Response, Router, get

from app import env


@get(path="/api-particulier/quotient", include_in_schema=False)
async def get_api_particulier_quotient(
    request: Request[Any, Any, Any],
) -> Response[Any]:
    """This endpoint "forwards" the request coming from the frontend (the app).

    API Particulier doesn't implement CORS, so the app can't directly query it.
    We thus have this endpoint to act as some kind of proxy.

    """
    response = httpx.get(
        f"{env.PUBLIC_API_PARTICULIER_BASE_URL}{env.PUBLIC_API_PARTICULIER_QUOTIENT_ENDPOINT}?recipient={env.PUBLIC_API_PARTICULIER_RECIPIENT_ID}",
        headers={"authorization": request.headers["authorization"]},
    )
    return Response(response.content, status_code=response.status_code)


data_router: Router = Router(
    path="/data",
    route_handlers=[
        get_api_particulier_quotient,
    ],
)
