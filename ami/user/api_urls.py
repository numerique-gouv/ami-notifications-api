from django.urls import path

from .api_views import registrations, unregister_legacy

urlpatterns = [
    path("users/registrations", registrations),
    path("users/registrations/<uuid:registration_id>", unregister_legacy),
]
