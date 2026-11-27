from django.urls import path

from ami.authentication import api_views

urlpatterns = [
    path("check-auth", api_views.check_auth),
    path("logout", api_views.logout),
    path("api/v1/users/login-data", api_views.user_login_data),
]
