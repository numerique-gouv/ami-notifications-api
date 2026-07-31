from django.urls import path

from .api_views import access_key

root_urlpatterns = [
    path("access-key", access_key),
]
