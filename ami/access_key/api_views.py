import asyncio

from django.conf import settings
from django.http import Http404, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django_ratelimit.core import is_ratelimited


@require_POST
@csrf_exempt
async def access_key(request):
    if not settings.WEB_APP_ACCESS_KEYS:
        raise Http404
    try:
        if request.POST["key"] in settings.WEB_APP_ACCESS_KEYS:
            return JsonResponse({}, status=200)
    except KeyError:
        pass
    if settings.WEB_APP_ACCESS_KEY_RATE_LIMIT:
        if is_ratelimited(
            request,
            group="access-key",
            key="ip",
            rate=settings.WEB_APP_ACCESS_KEY_RATE_LIMIT,
            increment=True,
        ):
            await asyncio.sleep(float(settings.WEB_APP_ACCESS_KEY_RATE_LIMIT_DELAY or 1))
    return JsonResponse({"err": "access denied"}, status=401)
