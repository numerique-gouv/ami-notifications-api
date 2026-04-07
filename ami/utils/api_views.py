from typing import cast

from django.conf import settings
from django.db import connection
from django.http import HttpResponse
from drf_spectacular.utils import extend_schema
from rest_framework.decorators import api_view
from rest_framework.response import Response

from ami.user.utils import build_fc_hash
from ami.utils.httpx import httpxClient
from ami.utils.serializers import RecipientFcHashSerializer


@api_view(["HEAD"])
def ping(request):
    return Response()


@api_view(["GET"])
def get_sector_identifier_url(request):
    redirect_uris: list[str] = [
        url.strip() for url in settings.SECTOR_IDENTIFIER_URL.strip().split("\n")
    ]
    return Response(redirect_uris)


@extend_schema(
    parameters=[RecipientFcHashSerializer],
)
@api_view(["GET"])
def _dev_utils_recipient_fc_hash(request) -> HttpResponse:
    serializer = RecipientFcHashSerializer(data=request.query_params)
    serializer.is_valid(raise_exception=True)
    data: dict = cast(dict, serializer.validated_data)

    given_name = data["given_name"]
    family_name = data["family_name"]
    birthdate = data["birthdate"]
    gender = data["gender"]
    birthplace = data.get("birthplace", "")
    birthcountry = data["birthcountry"]

    hashed_pivot_data: str = build_fc_hash(
        given_name=given_name,
        family_name=family_name,
        birthdate=birthdate,
        gender=gender,
        birthplace=birthplace,
        birthcountry=birthcountry,
    )
    return HttpResponse(hashed_pivot_data)


@api_view(["GET"])
def _dev_utils_review_apps(request) -> Response[list[dict[str, str | int]]]:
    """Returns a list of tuples: (review app url, pull request title)."""
    response = httpxClient.get(
        "https://api.github.com/repos/numerique-gouv/ami-notifications-api/pulls",
        params={"state": "open", "sort": "created", "per_page": 100},
        headers={
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    staging_app = {
        "url": "https://ami-back-staging.osc-fr1.scalingo.io/",
        "title": "Staging",
        "number": 0,
        "description": "Staging",
    }
    if response.status_code >= 400:
        # Possibly rate limited
        return Response([staging_app])

    json_data = response.json()
    review_apps = [
        {
            "url": f"https://ami-back-staging-pr{review_app['number']}.osc-fr1.scalingo.io/",
            "title": f"PR{review_app['number']}: {review_app['title']}",
            "number": review_app["number"],
            "description": review_app["body"],
        }
        for review_app in json_data
    ]
    return Response([staging_app] + review_apps)


@api_view(["GET"])
def _dev_health_db_pool(request) -> Response | None:
    """Returns database connection pool statistics for monitoring."""
    sql_query = """
          SELECT
              pid,
              usename,
              application_name,
              client_addr,
              state,
              query,
              EXTRACT(EPOCH FROM (now() - state_change)) as duration_seconds
          FROM pg_stat_activity
          WHERE datname = current_database()
          AND pid != pg_backend_pid()
          ORDER BY state_change
      """
    with connection.cursor() as cursor:
        cursor.execute(sql_query)
        columns = [col[0] for col in cursor.description]

        return Response(
            {
                "status": connection.connection.info.transaction_status.name,
                "connections": [dict(zip(columns, row)) for row in cursor.fetchall()],
            }
        )
