import os
import uuid
from typing import cast

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.conf import settings
from django.db.models import QuerySet
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED

from ami.authentication.decorators import ami_login_required
from ami.notification.tasks import push_notification
from ami.partner.auth import IsPartnerAuthenticated, PartnerBasicAuthentication
from ami.user.models import User
from ami.utils import sentry

from .models import Notification, NotificationEvent, ScheduledNotification
from .serializers import (
    NotificationReadSerializer,
    NotificationResponseSerializer,
    NotificationSerializer,
    PartnerNotificationCreateSerializer,
    ScheduledNotificationCreateSerializer,
    ScheduledNotificationDeleteSerializer,
    ScheduledNotificationResponseSerializer,
)


@api_view(["GET"])
@ami_login_required
def list_notifications(request: Request) -> Response[QuerySet[Notification]]:
    serializer = NotificationReadSerializer(data=request.query_params)
    serializer.is_valid(raise_exception=True)
    data: dict = cast(dict, serializer.validated_data)

    read = data["read"]
    if "read" in request.query_params:
        notifications: QuerySet[Notification] = Notification.objects.filter(
            user=request.ami_user, read=read
        ).order_by("-created_at")
    else:
        notifications: QuerySet[Notification] = Notification.objects.filter(
            user=request.ami_user
        ).order_by("-created_at")
    serialized = NotificationSerializer(notifications, many=True).data
    return Response(serialized)


@api_view(["PATCH"])
@ami_login_required
def read_notification(
    request: Request,
    notification_id: uuid.UUID,
) -> Response:
    serializer = NotificationReadSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    data: dict = cast(dict, serializer.validated_data)

    notification = get_object_or_404(Notification, id=notification_id, user=request.ami_user)
    notification.read = data["read"]
    notification.save()

    channel_layer = get_channel_layer()
    assert channel_layer is not None
    # More complex version than `async_to_sync`, but this won't work in tests: "is bound to another event loop"
    async_to_sync(channel_layer.group_send)(
        f"user_{notification.user.id}",
        {
            "type": "notification.event",
            "user_id": str(notification.user.id),
            "id": str(notification.id),
            "event": NotificationEvent.UPDATED,
        },
    )
    return Response(NotificationSerializer(notification).data)


@api_view(["GET"])
def get_notification_key(request: Request) -> HttpResponse:
    return HttpResponse(settings.CONFIG.get("VAPID_APPLICATION_SERVER_KEY", ""))


@api_view(["DELETE", "POST"])
@ami_login_required
def scheduled_notifications(request: Request) -> Response:
    if request.method == "DELETE":
        return delete_scheduled_notification(request)
    return create_scheduled_notification(request)


def create_scheduled_notification(
    request: Request,
) -> Response[ScheduledNotificationResponseSerializer]:
    serializer = ScheduledNotificationCreateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    data: dict = cast(dict, serializer.validated_data)

    existing_scheduled_notification = ScheduledNotification.objects.filter(
        reference=data["reference"], user=request.ami_user
    ).first()
    status_code = HTTP_200_OK
    if existing_scheduled_notification is None:
        # create scheduled notification
        scheduled_notification = ScheduledNotification.objects.create(
            user_id=request.ami_user.id, **data
        )
        status_code = HTTP_201_CREATED
        scheduled_notification.refresh_from_db()
    elif existing_scheduled_notification.sent_at is None:
        # update scheduled notification
        ScheduledNotification.objects.filter(id=existing_scheduled_notification.id).update(**data)
        scheduled_notification = existing_scheduled_notification
    else:
        # scheduled notification was already sent as a notification to user: don't change it
        scheduled_notification = existing_scheduled_notification

    response_serializer = ScheduledNotificationResponseSerializer(
        data={
            "scheduled_notification_id": scheduled_notification.id,
        }
    )
    response_serializer.is_valid(raise_exception=True)
    return Response(response_serializer.data, status=status_code)


def delete_scheduled_notification(request: Request) -> Response:
    serializer = ScheduledNotificationDeleteSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    data: dict = cast(dict, serializer.validated_data)

    scheduled_notification = ScheduledNotification.objects.filter(
        **data, user=request.ami_user
    ).first()

    if scheduled_notification is None:
        return Response(status=404)

    if scheduled_notification.sent_at is None:
        scheduled_notification.delete()

    return Response(status=204)


@extend_schema(
    methods=["POST"],
    request=PartnerNotificationCreateSerializer,
    responses={201: NotificationResponseSerializer},
)
@api_view(["POST"])
@authentication_classes([PartnerBasicAuthentication])
@permission_classes([IsPartnerAuthenticated])
def partner_create_notification(request: Request) -> Response[NotificationResponseSerializer]:
    current_partner = request.ami_partner
    ignore_unknown_user = os.getenv(
        "IGNORE_NOTIFICATION_REQUESTS_FOR_UNREGISTERED_USER", "False"
    ).lower() in ("true", "1", "t")

    serializer = PartnerNotificationCreateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    data: dict = cast(dict, serializer.validated_data)

    try:
        user = User.objects.get(fc_hash=data["recipient_fc_hash"])
    except User.DoesNotExist:
        user = None

    if user is None:
        if ignore_unknown_user:
            return Response(status=404)
        user = User.objects.create(fc_hash=data["recipient_fc_hash"])
        notification_send_status = False
    else:
        if ignore_unknown_user and user.last_logged_in is None:
            return Response(status=404)
        notification_send_status = user.last_logged_in is not None

    try_push = True
    if not data["try_push"] or user.last_logged_in is None:
        # don't push notification if not required or if user has never logged in on AMI
        try_push = False

    notification: Notification = Notification(
        user_id=user.id, **{k: v for k, v in data.items() if k != "recipient_fc_hash"}
    )
    if notification.content_icon is None:
        notification.content_icon = current_partner.icon or "fr-icon-mail-star-line"
    notification.partner_id = current_partner.id
    notification.send_status = notification_send_status
    notification.save()

    push_notification.enqueue(str(notification.id), try_push)

    sentry.add_counter("notification.request.processed")

    response_data = {
        "notification_id": notification.id,
        "notification_send_status": notification_send_status,
    }
    return Response(NotificationResponseSerializer(response_data).data, status=201)
