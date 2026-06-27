from django.urls import path

from .api_views import get_catalog

root_urlpatterns = [
    path("users/catalog/procedures", get_catalog),
]
