import asyncio
import uuid
from typing import cast

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.conf import settings
from django.db.models import QuerySet
from rest_framework import serializers
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response

from ami.authentication.decorators import ami_login_required
from ami.notification.push import push
from ami.user.models import User

from .models import Notification, NotificationEvent


@api_view(["GET"])
@ami_login_required
def list_notifications(request: Request) -> Response[QuerySet[Notification]]:
    read = request.query_params.get("read")
    if read is not None:
        read = read in ["t", "true", "True", "1"]
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
    data: dict = request.data if isinstance(request.data, dict) else {}
    if "read" not in data:
        return Response(status=400)
    read = data["read"]
    truthy = ["t", "true", "True", 1]
    falsy = ["f", "false", "False", 0]
    if read not in truthy and read not in falsy:
        return Response(
            {"extra": [{"message": "Input should be a valid boolean", "key": "read"}]},
            status=400,
        )
    read = read in truthy
    try:
        notification = Notification.objects.get(id=notification_id, user=request.ami_user)
    except Notification.DoesNotExist:
        return Response(status=404)
    notification.read = read
    notification.save()

    channel_layer = get_channel_layer()
    assert channel_layer is not None
    # More complex version than `async_to_sync`, but this won't work in tests: "is bound to another event loop"
    asyncio.get_event_loop().run_until_complete(
        channel_layer.group_send(
            f"user_{notification.user.id}",
            {
                "type": "notification.event",
                "user_id": str(notification.user.id),
                "id": str(notification.id),
                "event": NotificationEvent.UPDATED,
            },
        )
    )
    return Response(NotificationSerializer(notification).data)


@api_view(["GET"])
def get_notification_key(request: Request) -> Response[str]:
    return Response(settings.CONFIG.get("VAPID_APPLICATION_SERVER_KEY", ""))


class NotificationSerializer(serializers.ModelSerializer):
    # Remap the "user" field from the model to "user_id" in the serializer
    user_id = serializers.UUIDField(source="user.id")

    class Meta:
        exclude = [
            "user",
            "try_push",
            "updated_at",
            "partner_id",
            "sa_orm_sentinel",
            "send_date",
            "send_status",
        ]
        model = Notification


class NotificationResponseSerializer(serializers.Serializer):
    notification_id = serializers.UUIDField()
    notification_send_status = serializers.BooleanField()


@api_view(["POST"])
def admin_create_notification(request: Request) -> Response[NotificationResponseSerializer]:
    serializer = AdminNotificationCreateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    data: dict = cast(dict, serializer.validated_data)

    try:
        User.objects.get(id=data["user_id"])
    except User.DoesNotExist:
        return Response(status=404)

    notification: Notification = Notification.objects.create(**data)
    # TODO: this was done in a background task on litestar, migrate this to using celery?
    async_to_sync(push)(notification, True)

    response_data = {
        "notification_id": notification.id,
        "notification_send_status": True,
    }
    return Response(NotificationResponseSerializer(response_data).data, status=201)


class AdminNotificationCreateSerializer(serializers.Serializer):
    user_id = serializers.UUIDField()
    title = serializers.CharField(min_length=1, source="content_title")
    message = serializers.CharField(min_length=1, source="content_body")
    sender = serializers.CharField(min_length=1)
