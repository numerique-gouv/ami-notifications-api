from django.urls import path

from .api_views import get_services

root_urlpatterns = [
    path("users/data/services", get_services),
]
