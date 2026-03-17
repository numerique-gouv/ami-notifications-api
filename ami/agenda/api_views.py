import datetime
from concurrent.futures import Future, ThreadPoolExecutor
from typing import cast

from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response

from ami.agenda.data.holidays import (
    get_holidays_dates,
    get_public_holidays_catalog,
    get_school_holidays_catalog,
)
from ami.agenda.data.internal import get_elections_catalog
from ami.agenda.data.partners import get_psl_inventory
from ami.agenda.schemas import Agenda, AgendaCatalogStatus, FollowUp
from ami.agenda.serializers import AgendaQueryParamsSerializer, AgendaSerializer, FollowUpSerializer
from ami.authentication.decorators import ami_login_required
from ami.utils.schemas import (
    DurationExpiration,
    MonthlyExpiration,
    TimeUnit,
)

CATALOG_EXPIRATION_RULES = {
    "school_holidays": MonthlyExpiration(),
    "public_holidays": MonthlyExpiration(),
    "elections": DurationExpiration(amount=1, unit=TimeUnit.DAYS),
}


@api_view(["GET"])
@ami_login_required
def get_agenda_items(
    request: Request,
) -> Response[Agenda]:
    serializer = AgendaQueryParamsSerializer(data=request.query_params)
    serializer.is_valid(raise_exception=True)
    data: dict = cast(dict, serializer.validated_data)

    current_date: datetime.date = data["current_date"]
    filter_items: list[str] | None = data.get("filter_items")

    start_date, end_date = get_holidays_dates(current_date)
    agenda = Agenda()

    catalogs_mapping = {
        "school_holidays": get_school_holidays_catalog,
        "public_holidays": get_public_holidays_catalog,
        "elections": get_elections_catalog,
    }

    item_keys = filter_items or []
    item_keys = [f for f in item_keys if f in catalogs_mapping] or catalogs_mapping.keys()

    tasks: dict[str, Future] = {}
    with ThreadPoolExecutor() as executor:
        for catalog_name in item_keys:
            tasks[catalog_name] = executor.submit(
                catalogs_mapping[catalog_name],
                start_date=start_date,
                end_date=end_date,
            )

    for catalog_name in catalogs_mapping:
        if catalog_name not in item_keys:
            agenda.__dict__[catalog_name] = None
            continue
        result = tasks[catalog_name].result()
        if result.status == AgendaCatalogStatus.SUCCESS:
            result.set_expires_at(CATALOG_EXPIRATION_RULES[catalog_name])
        agenda.__dict__[catalog_name] = result
    return Response(AgendaSerializer(agenda).data)


@api_view(["GET"])
@ami_login_required
def get_follow_up_inventories(
    request: Request,
) -> Response[FollowUp]:
    follow_up = FollowUp()

    follow_up.psl = get_psl_inventory(current_user=request.ami_user)

    return Response(FollowUpSerializer(follow_up).data)
