from django.urls import path

from ami.fi import api_views

urlpatterns = [
    path("authorize/", api_views.authorize),
    path("token/", api_views.token),
    path("userinfo/", api_views.userinfo),
    path("logout/", api_views.logout),
]
