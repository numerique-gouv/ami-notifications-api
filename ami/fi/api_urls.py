from django.urls import path

from ami.fi import api_views, views

urlpatterns = [
    path("authorize/", views.authorize, name="ami-fi-authorize"),
    path("token/", api_views.token),
    path("userinfo/", api_views.userinfo),
    path("jwks/", api_views.jwks),
    path("logout/", api_views.logout),
    path("passkey/generate-registration-options", api_views.passkey_generate_registration_options),
    path("passkey/verify-registration", api_views.passkey_verify_registration),
    path(
        "passkey/generate-authentication-options", api_views.passkey_generate_authentication_options
    ),
    path("passkey/verify-authentication", api_views.passkey_verify_authentication),
]
