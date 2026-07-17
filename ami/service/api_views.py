from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response

from ami.authentication.decorators import ami_login_required
from ami.utils.schemas import DurationExpiration, TimeUnit

from .data.internal import get_internal_source
from .schemas import Services, ServicesSourceStatus
from .serializers import (
    ServicesItemsParametersSerializer,
    ServicesSerializer,
    get_parameters_values,
)

SOURCE_EXPIRATION_RULES = {
    "internal": DurationExpiration(amount=5, unit=TimeUnit.MINUTES),
}


@api_view(["GET"])
@ami_login_required
def get_services(request: Request) -> Response[Services]:
    service = Services()

    services_mapping = {
        "internal": get_internal_source,
    }

    for service_name in services_mapping:
        result = services_mapping[service_name]()
        if result.status == ServicesSourceStatus.SUCCESS:
            result.set_expires_at(SOURCE_EXPIRATION_RULES[service_name])
        service.__dict__[service_name] = result
    return Response(ServicesSerializer(service).data)


@api_view(["POST"])
@ami_login_required
def get_services_item_parameters(request: Request):
    serializer = ServicesItemsParametersSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    return Response(
        data={
            "data": get_parameters_values(
                validated_data=serializer.validated_data, user=request.ami_user
            )
        },
    )
