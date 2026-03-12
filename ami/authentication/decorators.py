import secrets
from base64 import b64decode
from functools import wraps

from django.http import JsonResponse

from ami.partner.models import partners


def ami_login_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.ami_user:
            return JsonResponse({}, status=401)
        return view_func(request, *args, **kwargs)

    return wrapper


def partner_auth_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        auth = request.headers.get("Authorization", "")
        if not auth:
            return JsonResponse({}, status=401)
        try:
            scheme, b64 = auth.split(" ", 1)
        except ValueError:
            return JsonResponse({}, status=401)
        if scheme.lower() != "basic":
            return JsonResponse({}, status=401)
        try:
            decoded = b64decode(b64, validate=True).decode("utf-8")
            partner_id, partner_secret = decoded.split(":", 1)
        except Exception:
            return JsonResponse({}, status=401)
        partner = partners.get(partner_id)
        if partner is None:
            return JsonResponse({}, status=401)
        if not secrets.compare_digest(partner.secret, partner_secret):
            return JsonResponse({}, status=401)
        request.partner = partner
        return view_func(request, *args, **kwargs)

    return wrapper
