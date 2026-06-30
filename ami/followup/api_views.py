from typing import cast

from django.http import Http404
from drf_spectacular.utils import extend_schema
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response

from ami.authentication.decorators import ami_login_required
from ami.notification.models import Notification

from .data.notification import get_notifications_source
from .schemas import Followup
from .serializers import (
    FollowupItemArchiveResponse,
    FollowupItemArchiveSerializer,
    FollowupSerializer,
)


@api_view(["GET"])
@ami_login_required
def get_followup(request: Request) -> Response[Followup]:
    followup = Followup()

    followup.notifications = get_notifications_source(current_user=request.ami_user)
    serializer = FollowupSerializer(followup)

    return Response(serializer.data)


@extend_schema(
    methods=["POST"],
    request=FollowupItemArchiveSerializer,
    responses={
        200: FollowupItemArchiveResponse,
    },
)
@api_view(["POST"])
@ami_login_required
def archive_followup_item(
    request: Request, source: str, item_external_id: str
) -> Response[FollowupItemArchiveResponse]:
    parts = item_external_id.split(":")
    if len(parts) != 3:
        raise Http404
    if not all(parts):
        raise Http404
    partner_id, item_type, item_id = parts

    if source != "notifications":
        raise Http404

    serializer = FollowupItemArchiveSerializer(data=request.data)
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
        .order_by("event_date", "created_at")
        .last()
    )
    if notification is None:
        raise Http404

    notification.item_is_archived = data["is_archived"]
    notification.save()

    response_data = {
        "source": source,
        "item_external_id": item_external_id,
        "is_archived": data["is_archived"],
    }
    return Response(FollowupItemArchiveResponse(response_data).data)
