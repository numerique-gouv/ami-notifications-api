from django.urls import path

from .api_views import archive_followup_item, get_followup

root_urlpatterns = [
    path("users/data/followup", get_followup),
    path(
        "users/data/followup/item/<str:source>/<str:item_external_id>/archive",
        archive_followup_item,
    ),
]
