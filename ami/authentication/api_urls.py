from django.urls import path

from .api_views import check_auth, logout

urlpatterns = [
    path("check-auth", check_auth),
    path("logout", logout),
]
