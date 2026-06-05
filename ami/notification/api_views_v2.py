from drf_spectacular.utils import extend_schema
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.request import Request
from rest_framework.response import Response

from ami.partner.auth import IsPartnerAuthenticated, PartnerBasicAuthentication

from .serializers import (
    NotificationResponseSerializer,
    PartnerEventCreateSerializerV2,
)


@extend_schema(
    methods=["PUT"],
    request=PartnerEventCreateSerializerV2,
    responses={
        200: NotificationResponseSerializer,
        201: NotificationResponseSerializer,
    },
)
@api_view(["PUT"])
@authentication_classes([PartnerBasicAuthentication])
@permission_classes([IsPartnerAuthenticated])
def partner_create_event(request: Request) -> Response[NotificationResponseSerializer]:
    return Response({}, status=201)
