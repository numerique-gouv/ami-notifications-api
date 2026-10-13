from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, schema
from rest_framework.request import Request
from rest_framework.response import Response

from ami.annuaire_sp.models import Mairie
from ami.authentication.decorators import ami_login_required
from ami.utils.schemas import DurationExpiration, TimeUnit


@api_view(["GET"])
@ami_login_required
@schema(None)
def get_mairie(
    request: Request,
    code_insee_commune: str,
) -> Response:
    mairie = get_object_or_404(Mairie, code_insee_commune=code_insee_commune)
    serialization = {
        "nom": mairie.nom,
        "url_service_public": mairie.url_service_public,
        "expires_at": DurationExpiration(amount=3, unit=TimeUnit.DAYS).compute_expires_at(),
    }
    return Response(serialization)
