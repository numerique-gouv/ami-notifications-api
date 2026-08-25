from django.urls import path

from .api_views import consent, registrations, unregister

urlpatterns = [
    path("users/registrations", registrations),
    path("users/registrations/<uuid:registration_id>", unregister),
    path("consent/<str:fc_hash>", consent),
]
