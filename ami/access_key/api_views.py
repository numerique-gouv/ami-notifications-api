from django.conf import settings
from django.http import Http404, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST


@require_POST
@csrf_exempt
def access_key(request):
    if not settings.WEB_APP_ACCESS_KEYS:
        raise Http404
    try:
        if request.POST["key"] in settings.WEB_APP_ACCESS_KEYS:
            return JsonResponse({}, status=200)
    except KeyError:
        pass
    return JsonResponse({"err": "access denied"}, status=401)
