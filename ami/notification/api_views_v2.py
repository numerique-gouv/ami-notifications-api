import logging
import os
from typing import cast

from drf_spectacular.utils import extend_schema
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.request import Request
from rest_framework.response import Response

from ami.partner.auth import IsPartnerAuthenticated, PartnerBasicAuthentication
from ami.user.models import Consent, User
from ami.utils import sentry

from .models import Notification, NotificationEvent
from .serializers import (
    NotificationResponseSerializer,
    PartnerEventCreateSerializerV2,
)

logger = logging.getLogger(__name__)


class PartnerCreateEventNotFoundException(Exception):
    pass


def partner_process_create_event_message(partner, data):
    current_partner = partner
    ignore_unknown_user = os.getenv(
        "IGNORE_NOTIFICATION_REQUESTS_FOR_UNREGISTERED_USER", "False"
    ).lower() in ("true", "1", "t")  # legacy, ignored when consent is enabled

    try:
        user = User.objects.get(fc_hash=data["recipient_fc_hash"])
    except User.DoesNotExist:
        user = None

    if current_partner.consent_is_enabled:
        if user is None:
            logger.info(f"User not found (partner {current_partner.id})")
            raise PartnerCreateEventNotFoundException("User not found")
        try:
            consent = Consent.objects.get(user=user, partner=current_partner)
        except Consent.DoesNotExist:
            logger.info(f"Consent not found (partner {current_partner.id})")
            raise PartnerCreateEventNotFoundException("Consent not found")
        if consent.consent_datetime is None:
            logger.info(f"Consent not given (partner {current_partner.id})")
            raise PartnerCreateEventNotFoundException("Consent not given")
    else:
        # legacy, will be removed when all partners are consent-ready
        if user is None:
            if ignore_unknown_user:
                logger.info("User not found")
                raise PartnerCreateEventNotFoundException("User not found")
            user = User.objects.create(fc_hash=data["recipient_fc_hash"])
        else:
            if ignore_unknown_user and user.last_logged_in is None:
                logger.info("User never seen")
                raise PartnerCreateEventNotFoundException("User never seen")

    notification_send_status = user.last_logged_in is not None
    try_push = True
    if not data["try_push"] or not notification_send_status:
        # don't push notification if not required or if user has never logged in on AMI
        try_push = False

    data.pop("recipient_fc_hash")
    notification, created = Notification.objects.get_or_create(
        user_id=user.id,
        partner=current_partner,
        defaults={"send_status": notification_send_status},
        **data,
    )
    if created:
        notification.push(event=NotificationEvent.CREATED, try_push=try_push)

    sentry.add_counter("notification.request.processed")

    response_data = {
        "notification_id": notification.id,
        "notification_send_status": notification_send_status,
    }
    return created, response_data


@extend_schema(
    methods=["PUT"],
    request=PartnerEventCreateSerializerV2,
    responses={
        200: NotificationResponseSerializer,
        201: NotificationResponseSerializer,
    },
    tags=["API partenaires"],
)
@api_view(["PUT"])
@authentication_classes([PartnerBasicAuthentication])
@permission_classes([IsPartnerAuthenticated])
def partner_create_event(request: Request) -> Response[NotificationResponseSerializer]:
    serializer = PartnerEventCreateSerializerV2(data=request.data, partner=request.ami_partner)
    serializer.is_valid(raise_exception=True)
    data: dict = cast(dict, serializer.validated_data)

    try:
        created, response_data = partner_process_create_event_message(request.ami_partner, data)
    except PartnerCreateEventNotFoundException as e:
        return Response({"error": str(e)}, status=404)

    return Response(
        NotificationResponseSerializer(response_data).data, status=201 if created else 200
    )
