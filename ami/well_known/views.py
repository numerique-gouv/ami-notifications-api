from django.conf import settings
from django.http import Http404, JsonResponse


def apple_app_site_association(request):
    if not settings.IOS_APP_IDS:
        raise Http404
    return JsonResponse(
        {
            "applinks": {
                "details": [
                    {
                        "appIDs": settings.IOS_APP_IDS,
                        "components": [
                            {
                                "?": {"no_universal_links": "*"},
                                "exclude": True,
                                "comment": "Opt out of universal links",
                            },
                            {"/": "*", "?": "*", "#": "*", "comment": "Matches any URL."},
                        ],
                    },
                ]
            },
            "webcredentials": {
                "apps": settings.IOS_APP_IDS,
            },
        }
    )
