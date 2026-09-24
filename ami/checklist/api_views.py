from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, schema
from rest_framework.request import Request
from rest_framework.response import Response

from ami.authentication.decorators import ami_login_required
from ami.checklist.models import CheckList


@api_view(["GET"])
@ami_login_required
@schema(None)
def get_checklist(
    request: Request,
    external_id: str,
) -> Response:
    checklist = get_object_or_404(CheckList, external_id=external_id)
    serialization = {"icon": checklist.icon, "definition": checklist.definition}
    return Response(serialization)
