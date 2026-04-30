from django.urls import include, path

from ami.agent_admin import api_views, manage_urls
from ami.agent_admin.views import base_views

app_name = "agent_admin"
urlpatterns = [
    path("oidc/", include("mozilla_django_oidc.urls")),
    path("", base_views.home, name="home"),
    path("login/", base_views.login, name="login"),
    path("access-denied/", base_views.access_denied, name="access-denied"),
    path("api/users/", api_views.users, name="api-users"),
    path("manage/", include(manage_urls, namespace="manage")),
]
