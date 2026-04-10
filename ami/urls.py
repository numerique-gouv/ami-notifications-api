from django.contrib import admin
from django.urls import include, path, re_path
from django.views.generic import TemplateView

from ami.agent_admin import urls as agent_admin_urls
from ami.api import urls as api_urls
from ami.authentication import urls as authentication_urls

urlpatterns = [
    path("ami-admin/", admin.site.urls),
    path("agent-admin/", include(agent_admin_urls, namespace="agent-admin")),
    path("", include(authentication_urls)),
    path("", include(api_urls)),
    re_path(
        r"^(?!"
        r"ami-admin/"
        r"agent-admin|"
        r"login-france-connect|"
        r"login-callback|"
        r"check-auth|"
        r"logout|"
        r"ping|"
        r"sector_identifier_url|"
        r"dev-utils/|"
        r"notification-key|"
        r"data|"
        r"api|"
        r"schema|"
        r"static/|"
        r"media/"
        r").*$",
        TemplateView.as_view(template_name="front/200.html"),
    ),
]
