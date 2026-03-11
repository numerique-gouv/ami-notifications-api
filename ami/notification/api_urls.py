from django.urls import path

from .api_views import list_notifications, read_notification

urlpatterns = [
    path("users/notifications", list_notifications),
    path("users/notification/<uuid:notification_id>/read", read_notification),
]
