from django.urls import path

from .api_views import get_page

urlpatterns = [
    path("page/<str:page_slug>", get_page),
]
