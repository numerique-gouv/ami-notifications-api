"""
ASGI config for ami project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/asgi/
"""

import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ami.settings")
django.setup()

from channels.routing import ProtocolTypeRouter, URLRouter  # noqa: E402
from django.core.asgi import get_asgi_application  # noqa: E402

from ami.authentication.middleware import AMIJWTAuthCookieASGIMiddleware  # noqa: E402
from ami.notification.channel_routing import websocket_urlpatterns  # noqa: E402

django_application = get_asgi_application()

application = ProtocolTypeRouter(
    {
        "http": django_application,
        "websocket": AMIJWTAuthCookieASGIMiddleware(URLRouter(websocket_urlpatterns)),
    }
)
