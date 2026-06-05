from django.urls import path

from .api_views_v2 import (
    partner_create_event,
)

urlpatterns = [
    path("event", partner_create_event),
]
