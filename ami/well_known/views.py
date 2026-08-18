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


def assetlinks(request):
    if not settings.ANDROID_PACKAGE_NAME:
        raise Http404
    return JsonResponse(
        [
            {
                "relation": [
                    "delegate_permission/common.handle_all_urls",
                    "delegate_permission/common.get_login_creds",
                ],
                "target": {
                    "namespace": "android_app",
                    "package_name": settings.ANDROID_PACKAGE_NAME,
                    "sha256_cert_fingerprints": settings.ANDROID_CERT_FINGERPRINTS,
                },
            }
        ],
        safe=False,
    )
