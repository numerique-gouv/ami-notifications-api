from django.urls import include, path
from django.views.generic import TemplateView

from ami.authentication import urls as authentication_urls
from ami.utils import api_urls as util_api_urls

urlpatterns = [
    path("", include(util_api_urls)),
    path("", include(authentication_urls)),
    path("", TemplateView.as_view(template_name="index.html")),
]
