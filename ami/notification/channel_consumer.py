import json

from channels.generic.websocket import AsyncWebsocketConsumer
from django.conf import settings


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user_id = self.scope.get("ami_user_id")
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

    async def notification_event(self, event: dict):
        await self.send(
            text_data=json.dumps(
                {
                    "user_id": event["user_id"],
                    "id": event["id"],
                    "event": event["event"],
                }
            )
        )
