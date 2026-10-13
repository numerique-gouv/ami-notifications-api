from django.urls import path

from .api_views import get_mairie

root_urlpatterns = [
    path("users/data/mairie/<str:code_insee_commune>", get_mairie),
]
