import uuid
from typing import cast

from django.shortcuts import get_object_or_404
from drf_spectacular.utils import PolymorphicProxySerializer, extend_schema, inline_serializer
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED

from ami.authentication.decorators import ami_login_required

from .models import Registration
from .serializers import (
    MobileAppSubscriptionSerializer,
    RegistrationCreateSerializer,
    RegistrationSerializer,
    WebPushSubscriptionSerializer,
)


@extend_schema(methods=["GET"], responses=RegistrationSerializer(many=True))
@extend_schema(
    methods=["POST"],
    request=PolymorphicProxySerializer(
        component_name="RegistrationCreate",
        serializers=[
            inline_serializer(
                "WebPushRegistrationCreate", {"subscription": WebPushSubscriptionSerializer()}
            ),
            inline_serializer(
                "MobileRegistrationCreate", {"subscription": MobileAppSubscriptionSerializer()}
            ),
        ],
        resource_type_field_name=None,
    ),
    responses={200: RegistrationSerializer, 201: RegistrationSerializer},
)
@api_view(["GET", "POST"])
@ami_login_required
def registrations(request: Request) -> Response:
    if request.method == "GET":
        regs = Registration.objects.filter(user=request.ami_user)
        return Response(RegistrationSerializer(regs, many=True).data)

    serializer = RegistrationCreateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    data: dict = cast(dict, serializer.validated_data)
    subscription: dict = data["subscription"]

    try:
        existing_registration: Registration | None = Registration.objects.get(
            subscription=subscription, user=request.ami_user
        )
        return Response(RegistrationSerializer(existing_registration).data)
    except Registration.DoesNotExist:
        pass

    registration: Registration = Registration.objects.create(
        user=request.ami_user, subscription=subscription
    )
    return Response(RegistrationSerializer(registration).data, status=HTTP_201_CREATED)


@api_view(["DELETE"])
@ami_login_required
def unregister(
    request: Request,
    registration_id: uuid.UUID,
) -> Response:
    registration: Registration | None = get_object_or_404(
        Registration, id=registration_id, user=request.ami_user
    )
    registration.delete()
    return Response(status=204)
