from django.urls import path

from ami.authentication import views

urlpatterns = [
    path("login-france-connect", views.login_france_connect),
    path("relogin-france-connect", views.relogin_france_connect),
    path("silent-login-ami-fi", views.silent_login_ami_fi),
    path("login-callback", views.login_callback),
]
