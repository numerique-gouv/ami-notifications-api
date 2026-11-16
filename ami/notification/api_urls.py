from django.urls import path

from .api_views import (
    list_notifications,
    partner_create_notification,
    read_notification,
    scheduled_notifications,
)

urlpatterns = [
    path("users/notifications", list_notifications),
    path("users/notification/<uuid:notification_id>/read", read_notification),
    path("notifications", partner_create_notification),
    path("users/scheduled-notifications", scheduled_notifications),
]
