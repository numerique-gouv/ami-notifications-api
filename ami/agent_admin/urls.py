from django.urls import include, path

from ami.agent_admin import views

app_name = "agent_admin"
urlpatterns = [
    path("oidc/", include("mozilla_django_oidc.urls")),
    path("", views.home, name="home"),
    path("login/", views.login, name="login"),
    path("access-denied/", views.access_denied, name="access-denied"),
    path("manage/access/", views.manage_access, name="manage-access"),
]
