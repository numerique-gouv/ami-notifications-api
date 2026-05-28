from django.conf import settings
from rest_framework.decorators import api_view
from rest_framework.response import Response

from ami.authentication.decorators import ami_login_required
from ami.authentication.models import RevokedAuthToken
from ami.authentication.schemas import data_providers


@api_view(["GET"])
@ami_login_required
def check_auth(request):
    return Response({"authenticated": True})


@api_view(["POST"])
@ami_login_required
def logout(request):
    if request.ami_payload.get("jti") is not None:
        RevokedAuthToken.objects.create(jti=request.ami_payload["jti"])
    response = Response({}, status=201)
    response.delete_cookie(settings.AUTH_COOKIE_JWT_NAME)
    response.delete_cookie(settings.USERINFO_COOKIE_JWT_NAME)
    return response


@api_view(["GET"])
def providers(request):
    data = {}
    for provider in data_providers.values():
        if not provider.is_enabled():
            continue
        data[provider.id] = provider.label
    return Response(data)
