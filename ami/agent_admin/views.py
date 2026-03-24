from django.shortcuts import render

from ami.agent.decorators import agent_login_required, role_admin_required, role_support_required
from ami.agent.models import Agent


@agent_login_required
@role_support_required
def home(request):
    return render(request, "agent_admin/home.html", {"agents": Agent.objects.all()})


def login(request):
    return render(request, "agent_admin/login.html", {})


@agent_login_required
def access_denied(request):
    return render(request, "agent_admin/access_denied.html", {})


@agent_login_required
@role_admin_required
def manage_access(request):
    return render(request, "agent_admin/manage_access.html", {})
