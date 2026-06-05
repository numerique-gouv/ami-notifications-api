import os
from functools import partial
from typing import cast

from django.db import transaction
from drf_spectacular.utils import extend_schema
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.request import Request
from rest_framework.response import Response

from ami.notification.tasks import push_notification
from ami.partner.auth import IsPartnerAuthenticated, PartnerBasicAuthentication
from ami.user.models import User
from ami.utils import sentry

from .models import Notification
from .serializers import (
    NotificationResponseSerializer,
    PartnerEventCreateSerializerV2,
)


def _partner_create_event(request: Request, data: dict):
    current_partner = request.ami_partner
    ignore_unknown_user = os.getenv(
        "IGNORE_NOTIFICATION_REQUESTS_FOR_UNREGISTERED_USER", "False"
    ).lower() in ("true", "1", "t")

    try:
        user = User.objects.get(fc_hash=data["recipient_fc_hash"])
    except User.DoesNotExist:
        user = None

    if user is None:
        if ignore_unknown_user:
            return Response({"error": "User not found"}, status=404)
        user = User.objects.create(fc_hash=data["recipient_fc_hash"])
        notification_send_status = False
    else:
        if ignore_unknown_user and user.last_logged_in is None:
            return Response({"error": "User never seen"}, status=404)
        notification_send_status = user.last_logged_in is not None

    try_push = True
    if not data["try_push"] or user.last_logged_in is None:
        # don't push notification if not required or if user has never logged in on AMI
        try_push = False

    data.pop("recipient_fc_hash")
    with transaction.atomic():
        notification, created = Notification.objects.get_or_create(
            user_id=user.id,
            partner_id=current_partner.id,
            defaults={"send_status": notification_send_status},
            **data,
        )
        if created:
            transaction.on_commit(
                partial(push_notification.enqueue, str(notification.id), try_push)  # type: ignore[union-attr]
            )

    sentry.add_counter("notification.request.processed")

    response_data = {
        "notification_id": notification.id,
        "notification_send_status": notification_send_status,
    }
    return Response(
        NotificationResponseSerializer(response_data).data, status=201 if created else 200
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
    serializer = PartnerEventCreateSerializerV2(data=request.data)
    serializer.is_valid(raise_exception=True)
    data: dict = cast(dict, serializer.validated_data)

    return _partner_create_event(request, data)
