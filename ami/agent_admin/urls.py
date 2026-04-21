from django.urls import include, path

from ami.agent_admin import api_views, views

app_name = "agent_admin"
urlpatterns = [
    path("oidc/", include("mozilla_django_oidc.urls")),
    path("", views.home, name="home"),
    path("login/", views.login, name="login"),
    path("access-denied/", views.access_denied, name="access-denied"),
    path("manage/access/", views.manage_access, name="manage-access"),
    path("notification/", views.send_notification, name="send-notification"),
    path("api/users/", api_views.users, name="api-users"),
]
