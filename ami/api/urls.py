from django.urls import include, path

from ami.authentication import api_urls as authentication_api_urls
from ami.notification import api_urls as notification_api_urls
from ami.partner import api_urls as partner_api_urls
from ami.user import api_urls as user_api_urls
from ami.utils import api_urls as util_api_urls

urlpatterns = [
    path("", include(authentication_api_urls)),
    path("", include(util_api_urls)),
    path("", include(notification_api_urls.root_urlpatterns)),
    path("api/v1/", include(notification_api_urls)),
    path("api/v1/", include(partner_api_urls)),
    path("api/v1/", include(user_api_urls)),
]
