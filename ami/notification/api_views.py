import asyncio
import uuid
from typing import cast

from channels.layers import get_channel_layer
from django.conf import settings
from django.db.models import QuerySet
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response

from ami.authentication.decorators import ami_login_required

from .models import Notification, NotificationEvent
from .serializers import (
    NotificationReadSerializer,
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
        fields = [
            "content_body",
            "content_icon",
            "content_title",
            "created_at",
            "id",
            "item_canal",
            "item_external_url",
            "item_generic_status",
            "item_id",
            "item_milestone_end_date",
            "item_milestone_start_date",
            "item_status_label",
            "item_type",
            "read",
            "sender",
            "user_id",
        ]
        model = Notification
