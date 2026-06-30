from django.urls import path

from .api_views import get_agenda

root_urlpatterns = [
    path("users/data/agenda", get_agenda),
]
