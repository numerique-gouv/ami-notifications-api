from typing import cast

from django.http import Http404
from drf_spectacular.utils import extend_schema
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response

from ami.authentication.decorators import ami_login_required
from ami.notification.models import Notification

from .data.notification import get_notifications_inventory
from .schemas import FollowUp
from .serializers import (
    FollowUpItemArchiveResponse,
    FollowUpItemArchiveSerializer,
    FollowUpSerializer,
)


@api_view(["GET"])
@ami_login_required
def get_follow_up_inventories(request: Request) -> Response[FollowUp]:
    follow_up = FollowUp()

    follow_up.notifications = get_notifications_inventory(current_user=request.ami_user)
    serializer = FollowUpSerializer(follow_up)

    return Response(serializer.data)


@extend_schema(
    methods=["POST"],
    request=FollowUpItemArchiveSerializer,
    responses={
        200: FollowUpItemArchiveResponse,
    },
)
@api_view(["POST"])
@ami_login_required
def archive_followup_item(
    request: Request, inventory: str, item_external_id: str
) -> Response[FollowUpItemArchiveResponse]:
    parts = item_external_id.split(":")
    if len(parts) != 3:
        raise Http404
    if not all(parts):
        raise Http404
    partner_id, item_type, item_id = parts

    if inventory != "notifications":
        raise Http404

    serializer = FollowUpItemArchiveSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    data: dict = cast(dict, serializer.validated_data)

    notification = (
        Notification.objects.filter(
            item_generic_status__isnull=False,
            item_status_label__isnull=False,
            item_type__isnull=False,
            item_id__isnull=False,
            user=request.ami_user,
            partner_id=partner_id,
            item_type=item_type,
            item_id=item_id,
        )
        .order_by("send_date", "created_at")
        .last()
    )
    if notification is None:
        raise Http404

    notification.item_is_archived = data["is_archived"]
    notification.save()

    response_data = {
        "inventory": inventory,
        "item_external_id": item_external_id,
        "is_archived": data["is_archived"],
    }
    return Response(FollowUpItemArchiveResponse(response_data).data)
