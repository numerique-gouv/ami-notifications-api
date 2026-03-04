from django.urls import re_path

from ami.notification.channel_consumer import NotificationConsumer

websocket_urlpatterns = [
    re_path(r"api/v1/users/notification/events/stream", NotificationConsumer.as_asgi()),  # type: ignore[arg-type]
]
