from django.urls import include, path
from django.views.generic import TemplateView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from ami.agenda import api_urls as agenda_api_urls
from ami.authentication import api_urls as authentication_api_urls
from ami.notification import api_urls as notification_api_urls
from ami.partner import api_urls as partner_api_urls
from ami.user import api_urls as user_api_urls
from ami.utils import api_urls as util_api_urls

urlpatterns = [
    path("", include(authentication_api_urls)),
    path("", include(util_api_urls)),
    path("", include(notification_api_urls.root_urlpatterns)),
    path("", include(agenda_api_urls.root_urlpatterns)),
    path("api/v1/", include(notification_api_urls)),
    path("api/v1/", include(partner_api_urls)),
    path("api/v1/", include(user_api_urls)),
    # drf-spectacular
    path("api/v1/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/v1/schema/swagger-ui/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path(
        "api/v1/schema/rapidoc/",
        TemplateView.as_view(
            template_name="rapidoc.html",
            extra_context={"schema_url": "/api/v1/schema/"},
        ),
    ),
]
