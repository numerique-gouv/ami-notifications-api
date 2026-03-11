from django.urls import path

from .api_views import list_notifications

urlpatterns = [
    path("users/notifications", list_notifications),
]
