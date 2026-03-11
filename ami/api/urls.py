from django.urls import include, path

from ami.authentication import api_urls as authentication_api_urls
from ami.notification import api_urls as notification_api_urls
from ami.utils import api_urls as util_api_urls

urlpatterns = [
    path("", include(authentication_api_urls)),
    path("", include(util_api_urls)),
    path("api/v1/", include(notification_api_urls)),
]
