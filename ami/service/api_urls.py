from django.urls import path

from .api_views import get_services, get_services_item_parameters

root_urlpatterns = [
    path("users/data/services", get_services),
    path("users/data/services/item/parameters", get_services_item_parameters),
]
