import datetime
from concurrent.futures import Future, ThreadPoolExecutor
from typing import cast

from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response

from ami.agenda.data.holidays import (
    get_holidays_dates,
    get_public_holidays_source,
    get_school_holidays_source,
)
from ami.agenda.data.internal import get_elections_source
from ami.agenda.schemas import Agenda, AgendaSourceStatus
from ami.agenda.serializers import AgendaQueryParamsSerializer, AgendaSerializer
from ami.authentication.decorators import ami_login_required
from ami.utils.schemas import DurationExpiration, MonthlyExpiration, TimeUnit

SOURCE_EXPIRATION_RULES = {
    "school_holidays": MonthlyExpiration(),
    "public_holidays": MonthlyExpiration(),
    "elections": DurationExpiration(amount=1, unit=TimeUnit.DAYS),
}


@api_view(["GET"])
@ami_login_required
def get_agenda(
    request: Request,
) -> Response[Agenda]:
    serializer = AgendaQueryParamsSerializer(data=request.query_params)
    serializer.is_valid(raise_exception=True)
    data: dict = cast(dict, serializer.validated_data)

    current_date: datetime.date = data["current_date"]
    filter_items: list[str] | None = data.get("filter_items")

    start_date, end_date = get_holidays_dates(current_date)
    agenda = Agenda()

    sources_mapping = {
        "school_holidays": get_school_holidays_source,
        "public_holidays": get_public_holidays_source,
        "elections": get_elections_source,
    }

    item_keys = filter_items or []
    item_keys = [f for f in item_keys if f in sources_mapping] or sources_mapping.keys()

    tasks: dict[str, Future] = {}
    with ThreadPoolExecutor() as executor:
        for source_name in item_keys:
            tasks[source_name] = executor.submit(
                sources_mapping[source_name],
                start_date=start_date,
                end_date=end_date,
            )

    for source_name in sources_mapping:
        if source_name not in item_keys:
            agenda.__dict__[source_name] = None
            continue
        result = tasks[source_name].result()
        if result.status == AgendaSourceStatus.SUCCESS:
            result.set_expires_at(SOURCE_EXPIRATION_RULES[source_name])
        agenda.__dict__[source_name] = result
    return Response(AgendaSerializer(agenda).data)
