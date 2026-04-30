from django.http import JsonResponse
from rest_framework.decorators import api_view, schema

from ami.agent.decorators import agent_login_required, role_notifications_required
from ami.user.models import User


@agent_login_required
@role_notifications_required
@api_view(["GET"])
@schema(None)
def users(request) -> JsonResponse:
    queryset = User.objects.none()
    if request.GET.get("q"):
        queryset = User.objects.filter(
            fc_hash__startswith=request.GET["q"],
        ).order_by("fc_hash")[:10]
    result = [{"value": user.fc_hash} for user in queryset]
    return JsonResponse({"data": result})
