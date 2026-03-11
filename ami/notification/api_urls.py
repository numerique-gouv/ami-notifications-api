from django.urls import path

from .api_views import (
    admin_create_notification,
    get_notification_key,
    list_notifications,
    read_notification,
)

urlpatterns = [
    path("users/notifications", list_notifications),
    path("users/notification/<uuid:notification_id>/read", read_notification),
]

root_urlpatterns = [
    path("notification-key", get_notification_key),
    path("ami_admin/notifications", admin_create_notification),
]
