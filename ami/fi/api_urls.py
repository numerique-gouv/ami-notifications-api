from django.urls import path

from ami.fi import api_views, views

urlpatterns = [
    path("authorize/", views.authorize, name="ami-fi-authorize"),
    path("token/", api_views.token),
    path("userinfo/", api_views.userinfo),
    path("logout/", api_views.logout),
]
