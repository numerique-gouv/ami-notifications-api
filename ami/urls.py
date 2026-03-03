from django.urls import include, path
from django.views.generic import TemplateView

from ami.authentication import urls as authentication_urls
from ami.utils import views as ami_views

urlpatterns = [
    path("ping", ami_views.ping),
    path("", include(authentication_urls)),
    path("", TemplateView.as_view(template_name="index.html")),
]
