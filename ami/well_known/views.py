from django.conf import settings
from django.http import Http404, JsonResponse


def apple_app_site_association(request):
    if not settings.IOS_APP_IDS:
        raise Http404
    return JsonResponse(
        {
            "webcredentials": {
                "apps": settings.IOS_APP_IDS,
            },
        }
    )
