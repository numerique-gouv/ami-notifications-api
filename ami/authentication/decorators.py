from functools import wraps

from django.http import JsonResponse


def ami_login_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.ami_user:
            return JsonResponse({}, status=401)
        return view_func(request, *args, **kwargs)

    return wrapper
