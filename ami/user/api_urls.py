from django.urls import path

from .api_views import consent, consents, registrations, unregister_legacy

urlpatterns = [
    path("users/registrations", registrations),
    path("users/registrations/<uuid:registration_id>", unregister_legacy),
    path("consent/<str:fc_hash>", consent),
    path("users/consents", consents),
]
