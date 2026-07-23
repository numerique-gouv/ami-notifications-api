from django.shortcuts import render

from ami.agent.decorators import (
    agent_login_required,
    role_admin_required,
)
from ami.service.models import Service


@agent_login_required
@role_admin_required
def list_services(request):
    context = {
        "object_list": Service.objects.all().order_by("title"),
    }
    return render(request, "agent_admin/manage/list_services.html", context)
