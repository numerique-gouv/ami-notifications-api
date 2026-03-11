import asyncio
import uuid

from channels.layers import get_channel_layer
from django.db.models import QuerySet
from rest_framework import serializers
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response

from ami.authentication.decorators import ami_login_required

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
