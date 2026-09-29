from django.urls import path

from .api_views import (
    consent,
    consents,
    consents_all,
    personal_data_consent,
    registrations,
    unregister_legacy,
)

urlpatterns = [
    path("users/registrations", registrations),
    path("users/registrations/<uuid:registration_id>", unregister_legacy),
    path("consent/<str:fc_hash>", consent),
    path("users/consents", consents),
    path("users/consents/all", consents_all),
    path("users/personal-data-consent", personal_data_consent),
]
