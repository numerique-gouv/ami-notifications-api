from django.urls import path

from .api_views import get_follow_up_inventories

root_urlpatterns = [
    path("users/follow-up/inventories", get_follow_up_inventories),
]
