from django.urls import path

from .api_views import (
    generate_partner_url,
    get_partner_public_key,
)

urlpatterns = [
    path("partner/otv/url", generate_partner_url),
    path("partner/otv/public_key", get_partner_public_key),
]
