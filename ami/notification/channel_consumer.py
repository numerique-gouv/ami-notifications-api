import json
from http.cookies import SimpleCookie

import jwt
from channels.generic.websocket import AsyncWebsocketConsumer
from django.conf import settings
from jwt import InvalidTokenError


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        print("CONNECTING")
        user_id = self._authenticate()
        if user_id is None:
            await self.close(code=settings.PUBLIC_CHANNEL_UNAUTHORIZED_CODE)
            return

        assert self.channel_layer is not None, "CHANNEL_LAYERS is not configured"
        self.group_name = f"user_{user_id}"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, code: int):
        if hasattr(self, "group_name"):
            assert self.channel_layer is not None
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def notification_event(self, event):
        await self.send(
            text_data=json.dumps(
                {
                    "user_id": event["user_id"],
                    "id": event["id"],
                    "event": event["event"],
                }
            )
        )

    def _authenticate(self) -> str | None:
        """Get the user_id from the token sub. The token is provided in a cookie."""
        # TODO: when we have a proper auth middleware for our JWT login setup in the ami/asgi.py file,
        # remove this method, and access the user with `user = self.scope["user"]` in `connect() above`.
        for name, value in self.scope.get("headers", []):
            if name == b"cookie":
                cookie = SimpleCookie(value.decode())
                token = cookie.get("token")
                if token is None:
                    return None
                try:
                    payload = jwt.decode(
                        token.value.removeprefix("Bearer "),
                        settings.AUTH_COOKIE_JWT_SECRET,
                        algorithms=["HS256"],
                    )
                    return payload.get("sub")
                except InvalidTokenError:
                    return None
        return None
