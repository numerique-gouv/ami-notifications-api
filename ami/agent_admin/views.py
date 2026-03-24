from django.shortcuts import render

from ami.agent.decorators import agent_login_required, role_admin_required, role_support_required
from ami.agent.models import Agent


@agent_login_required
@role_support_required
def home(request):
    return render(request, "agent_admin/home.html", {})


def login(request):
    return render(request, "agent_admin/login.html", {})


@agent_login_required
def logout(request):
    return render(request, "agent_admin/logout.html", {})


@agent_login_required
def access_denied(request):
    return render(request, "agent_admin/access_denied.html", {})


@agent_login_required
@role_admin_required
def manage_access(request):
    unauthorized_agents = Agent.objects.filter(role__isnull=True).order_by("-proconnect_last_login")
    authorized_agents = Agent.objects.filter(role__isnull=False).order_by(
        "user__last_name",
        "user__first_name",
    )
    context = {
        "unauthorized_agents": unauthorized_agents,
        "authorized_agents": authorized_agents,
        "roles": Agent.Role,
    }
    return render(request, "agent_admin/manage_access.html", context)
