from django.urls import path

from .api_views import get_trusted_urls

root_urlpatterns = [
    path("users/data/trusted_urls", get_trusted_urls),
]
