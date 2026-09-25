from django.conf import settings
from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.request import Request

from ami.authentication.decorators import ami_login_required


@api_view(["GET"])
@ami_login_required
def get_trusted_urls(request: Request) -> JsonResponse:
    if not settings.TRUSTED_URLS:
        return JsonResponse({"trusted_urls": []})

    trusted_urls = settings.TRUSTED_URLS.split(",")

    return JsonResponse({"trusted_urls": trusted_urls})
