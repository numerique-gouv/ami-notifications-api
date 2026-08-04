from django.urls import path

from ami.authentication import views

urlpatterns = [
    path("login-france-connect", views.login_france_connect),
    path("login-ami-fi", views.login_ami_fi),
    path("silent-login-ami-fi", views.silent_login_ami_fi),
    path("login-callback", views.login_callback),
    path("generate-registration-options", views.passkey_generate_registration_options),
    path("verify-registration", views.passkey_verify_registration),
]
