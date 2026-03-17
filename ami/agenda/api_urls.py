from django.urls import path

from .api_views import (
    get_agenda_items,
    get_follow_up_inventories,
)

urlpatterns = [
    path("agenda/items", get_agenda_items),
    path("follow-up/inventories", get_follow_up_inventories),
]
