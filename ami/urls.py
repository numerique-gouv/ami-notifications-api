from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView

from ami.agent_admin import urls as agent_admin_urls
from ami.api import urls as api_urls
from ami.authentication import urls as authentication_urls


class MobileAppView(TemplateView):
    def get_template_names(self):
        subpath = self.kwargs.get("subpath", "")
        return [f"{subpath}/index.html"] if subpath else ["index.html"]


urlpatterns = [
    path("ami-admin/", admin.site.urls),
    path("agent-admin/", include(agent_admin_urls, namespace="agent-admin")),
    path("", include(authentication_urls)),
    path("", include(api_urls)),
    path("<path:subpath>/", MobileAppView.as_view()),
    path("", MobileAppView.as_view()),
]
