from django.urls import include, path
from django.views.generic import TemplateView

from ami.agent_admin import urls as agent_admin_urls
from ami.api import urls as api_urls
from ami.authentication import urls as authentication_urls

urlpatterns = [
    path("", include(authentication_urls)),
    path("", include(api_urls)),
    path("", TemplateView.as_view(template_name="index.html")),
    path("agent-admin/", include(agent_admin_urls, namespace="agent-admin")),
]
