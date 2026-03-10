from django.urls import path

from .api_views import (
    _dev_health_db_pool,
    _dev_utils_recipient_fc_hash,
    _dev_utils_review_apps,
    get_sector_identifier_url,
    ping,
)

urlpatterns = [
    path("ping", ping),
    path("sector_identifier_url", get_sector_identifier_url),
    path("dev-utils/recipient-fc-hash", _dev_utils_recipient_fc_hash),
    path("dev-utils/review-apps", _dev_utils_review_apps),
    path("dev-utils/health/db-pool", _dev_health_db_pool),
]
