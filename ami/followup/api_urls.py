from django.urls import path

from .api_views import archive_followup_item, get_follow_up_inventories

root_urlpatterns = [
    path("users/follow-up/inventories", get_follow_up_inventories),
    path(
        "users/follow-up/item/<str:inventory>/<str:item_external_id>/archive", archive_followup_item
    ),
]
