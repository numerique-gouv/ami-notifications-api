"""
ASGI config for ami project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/asgi/
"""

import os

from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

from ami.notification.channel_routing import websocket_urlpatterns

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ami.settings")

django_application = get_asgi_application()

application = ProtocolTypeRouter(
    {
        "http": django_application,
        # TODO: when we have a proper auth middleware for our JWT login, use it here also
        "websocket": URLRouter(websocket_urlpatterns),
    }
)
