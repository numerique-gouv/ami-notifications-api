import secrets
from base64 import b64decode
from http.cookies import SimpleCookie

from channels.db import database_sync_to_async
from django.conf import settings

from ami.authentication.auth import decode_jwt_token
from ami.authentication.models import RevokedAuthToken
from ami.partner.models import partners
from ami.user.models import User


class AMIJWTAuthCookieASGIMiddleware:
    """Channels ASGI middleware that authenticates WebSocket connections via JWT cookie.

    Populates scope["ami_user_id"] with the authenticated user's ID, or None.
    """

    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):
        if scope["type"] == "websocket":
            scope["ami_user_id"] = await self._get_user_id(scope)
        await self.inner(scope, receive, send)

    async def _get_user_id(self, scope) -> str | None:
        for name, value in scope.get("headers", []):
            if name == b"cookie":
                cookie = SimpleCookie(value.decode())
                token_morsel = cookie.get(settings.AUTH_COOKIE_JWT_NAME)
                if token_morsel is None:
                    return None
                token = token_morsel.value.removeprefix("Bearer ")
                payload = decode_jwt_token(token)
                if not payload:
                    return None
                jti = payload.get("jti")
                if (
                    jti
                    and await database_sync_to_async(
                        RevokedAuthToken.objects.filter(jti=jti).exists
                    )()
                ):
                    return None
                return payload.get("sub")
        return None


class AMIJWTAuthCookieMiddleware:
    """WSGI middleware that authenticates http requests via JWT cookie.

    Populates request.ami_user and request.ami_payload.
    """

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


class AMIBasicPartnerAuthMiddleware:
    """WSGI middleware that authenticates http requests via basic auth for partners.

    Populates request.ami_partner.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.ami_partner = None
        header: str = request.headers.get("Authorization", "")

        try:
            scheme, b64 = header.split(" ", 1)
        except ValueError:
            return self.get_response(request)
        if scheme.lower() != "basic":
            return self.get_response(request)
        try:
            decoded = b64decode(b64, validate=True).decode("utf-8")
            partner_id, partner_secret = decoded.split(":", 1)
        except Exception:
            return self.get_response(request)
        partner = partners.get(partner_id)
        if partner and secrets.compare_digest(partner.secret, partner_secret):
            request.ami_partner = partner
        return self.get_response(request)
