from django.conf import settings

from ami.authentication.auth import decode_jwt_token
from ami.authentication.models import RevokedAuthToken
from ami.user.models import User


class AMIJWTAuthCookieMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        token = request.COOKIES.get(settings.AUTH_COOKIE_JWT_NAME)
        if not token:
            token = request.headers.get("Authorization", "")
        if token.startswith("Bearer "):
            token = token[7:]

        request.ami_payload = None
        request.ami_user = None

        if token:
            payload = decode_jwt_token(token)
            if payload:
                jti = payload.get("jti")
                is_revoked = False
                if jti and RevokedAuthToken.objects.filter(jti=jti).exists():
                    is_revoked = True
                if not is_revoked:
                    try:
                        request.ami_user = User.objects.get(id=payload["sub"])
                        request.ami_payload = payload
                    except User.DoesNotExist:
                        pass

        return self.get_response(request)
