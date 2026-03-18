from django.urls import path

from .api_views import (
    get_notification_key,
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

root_urlpatterns = [
    path("notification-key", get_notification_key),
]
