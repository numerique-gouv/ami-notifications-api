from django.urls import path

from ami.authentication import views

urlpatterns = [
    path("login-france-connect", views.login_france_connect),
    path("login-ami-fi", views.login_ami_fi),
    path("login-callback", views.login_callback),
]
