from django.urls import path

from .api_views import get_agenda_items

root_urlpatterns = [
    path("users/agenda/items", get_agenda_items),
]
