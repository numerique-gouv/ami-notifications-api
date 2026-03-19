from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response

from ami.authentication.decorators import ami_login_required

from .data.notification import get_psl_inventory
from .schemas import FollowUp
from .serializers import FollowUpSerializer


@api_view(["GET"])
@ami_login_required
def get_follow_up_inventories(request: Request) -> Response[FollowUp]:
    follow_up = FollowUp()

    follow_up.psl = get_psl_inventory(current_user=request.ami_user)
    serializer = FollowUpSerializer(follow_up)

    return Response(serializer.data)
