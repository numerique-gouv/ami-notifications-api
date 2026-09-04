import logging
import uuid
from typing import cast

from django.db import transaction
from django.db.models import QuerySet
from django.shortcuts import get_object_or_404
from django.utils.timezone import now
from drf_spectacular.utils import PolymorphicProxySerializer, extend_schema, inline_serializer
from rest_framework import serializers
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED

from ami.authentication.decorators import ami_login_required

from ..partner.auth import IsPartnerAuthenticated, PartnerBasicAuthentication
from .models import Consent, Registration, User
from .serializers import (
    ConsentPostResponseSerializer,
    ConsentPostSerializer,
    ConsentResponseSerializer,
    ConsentSerializer,
    ConsentUpdateSerializer,
    MobileAppSubscriptionSerializer,
    RegistrationCreateSerializer,
    RegistrationPutActionSerializer,
    RegistrationRemoveFromDeviceIdSerializer,
    RegistrationSerializer,
    WebPushSubscriptionSerializer,
)

logger = logging.getLogger(__name__)


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
@extend_schema(
    methods=["PUT"],
    parameters=[
        RegistrationPutActionSerializer,
    ],
    request=RegistrationRemoveFromDeviceIdSerializer,
)
@api_view(["GET", "POST", "PUT"])
@ami_login_required
def registrations(request: Request) -> Response:
    if request.method == "GET":
        regs = Registration.objects.filter(user=request.ami_user)
        return Response(RegistrationSerializer(regs, many=True).data)

    if request.method == "PUT":
        serializer = RegistrationPutActionSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        serializer = RegistrationRemoveFromDeviceIdSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        payload_data: dict = cast(dict, serializer.validated_data)

        registrations = Registration.objects.filter(device_id=payload_data["device_id"])
        if not registrations.exists():
            logger.error("No registration for the device_id: %s", payload_data["device_id"])
            return Response(status=404)
        registrations.delete()  # TODO: archive instead of delete?
        return Response(status=200)

    serializer = RegistrationCreateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    data: dict = cast(dict, serializer.validated_data)
    subscription: dict = data["subscription"]

    if "device_id" in subscription:
        with transaction.atomic():
            # In case of a mobile app subscription, check if we already have registration(s) for this device.
            existing_registrations: QuerySet[Registration] = Registration.objects.filter(
                subscription__device_id=subscription["device_id"],
            )
            registrations_exists = existing_registrations.exists()
            status = HTTP_200_OK if registrations_exists else HTTP_201_CREATED
            if registrations_exists:
                # and if so, delete them: we only want to keep the latest registration for a given device.
                existing_registrations.delete()
            registration: Registration = Registration.objects.create(
                user=request.ami_user,
                subscription=subscription,
                device_id=subscription["device_id"],
            )
        return Response(RegistrationSerializer(registration).data, status=status)

    try:
        existing_registration: Registration = Registration.objects.get(
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
def unregister_legacy(
    request: Request,
    registration_id: uuid.UUID,
) -> Response:
    registration: Registration | None = get_object_or_404(
        Registration, id=registration_id, user=request.ami_user
    )
    registration.delete()  # TODO: archive instead of delete?
    return Response(status=204)


@extend_schema(
    tags=["API partenaires"],
    description="""Returns the date the consent was given (consent_datetime).

If the fc_hash does not exist, or if consent has not been given, returns a null consent_datetime and a 404.""",
    summary="GET /api/v1/consent/{fc_hash}",
    methods=["GET"],
    responses={
        200: ConsentResponseSerializer,
    },
)
@extend_schema(
    tags=["API partenaires"],
    methods=["POST"],
    request=ConsentPostSerializer,
    responses={
        200: ConsentPostResponseSerializer,
    },
)
@api_view(["GET", "POST"])
@authentication_classes([PartnerBasicAuthentication])
@permission_classes([IsPartnerAuthenticated])
def consent(request: Request, fc_hash: str) -> Response:
    partner = request.ami_partner

    if request.method == "GET":
        consent = Consent.objects.filter(user__fc_hash=fc_hash, partner=partner).first()
        consent_datetime = consent.consent_datetime if consent else None

        response_serializer = ConsentResponseSerializer({"consent_datetime": consent_datetime})
        return Response(response_serializer.data, status=200 if consent_datetime else 404)

    serializer = ConsentPostSerializer(data=request.data)
    try:
        serializer.is_valid(raise_exception=True)
    except serializers.ValidationError:
        logger.exception("Partner post consent serialization error")
        raise
    data: dict = cast(dict, serializer.validated_data)

    user, _ = User.objects.get_or_create(fc_hash=fc_hash)
    consent_datetime = now() if data["consent"] else None
    Consent.objects.update_or_create(
        user=user,
        partner=partner,
        defaults={"consent_datetime": consent_datetime},
        create_defaults={"consent_datetime": consent_datetime},
    )

    response_serializer = ConsentPostResponseSerializer(
        {"message": "Consent given" if data["consent"] else "Consent withdrawn"}
    )
    return Response(response_serializer.data)


@extend_schema(
    methods=["POST"],
    request=ConsentUpdateSerializer,
)
@api_view(["GET", "POST"])
@ami_login_required
def consents(request: Request) -> Response:
    if request.method == "GET":
        consents_qs: QuerySet[Consent] = request.ami_user.consent_set.all().select_related(
            "partner"
        )
        return Response(ConsentSerializer(consents_qs, many=True).data)

    serializer = ConsentUpdateSerializer(data=request.data)
    try:
        serializer.is_valid(raise_exception=True)
    except serializers.ValidationError:
        logger.exception("Internal post consent serialization error")
        raise
    data: dict = cast(dict, serializer.validated_data)

    consent_datetime = now() if data["consent"] else None
    Consent.objects.update_or_create(
        user=request.ami_user,
        partner_id=data["partner_id"],
        defaults={"consent_datetime": consent_datetime},
        create_defaults={"consent_datetime": consent_datetime},
    )

    response_serializer = ConsentPostResponseSerializer(
        {"message": "Consent given" if data["consent"] else "Consent withdrawn"}
    )
    return Response(response_serializer.data)
