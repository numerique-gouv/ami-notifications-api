from django.urls import path

from .api_views import get_checklist

root_urlpatterns = [
    path("users/data/checklist/<str:external_id>", get_checklist),
]
