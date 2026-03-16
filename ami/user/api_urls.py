from django.urls import path

from .api_views import registrations, unregister

urlpatterns = [
    path("users/registrations", registrations),
    path("users/registrations/<uuid:registration_id>", unregister),
]
