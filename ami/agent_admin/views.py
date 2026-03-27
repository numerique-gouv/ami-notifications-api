from django.shortcuts import redirect, render
from django.urls import reverse

from ami.agent.decorators import agent_login_required, role_admin_required, role_support_required
from ami.agent.models import Agent
from ami.agent_admin.forms import AgentFormSet


@agent_login_required
@role_support_required
def home(request):
    return render(request, "agent_admin/home.html", {"agents": Agent.objects.all()})


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

    if request.method == "POST":
        unauthorized_agents_formset = AgentFormSet(
            request.POST, queryset=unauthorized_agents, prefix="unauthorized"
        )
        authorized_agents_formset = AgentFormSet(
            request.POST, queryset=authorized_agents, prefix="authorized"
        )
        is_unauthorized_agents_formset_valid = unauthorized_agents_formset.is_valid()
        is_authorized_agents_formset_valid = authorized_agents_formset.is_valid()
        if is_unauthorized_agents_formset_valid and is_authorized_agents_formset_valid:
            unauthorized_agents_formset.save()
            authorized_agents_formset.save()
            return redirect(reverse("agent-admin:manage-access"))
    else:
        unauthorized_agents_formset = AgentFormSet(
            queryset=unauthorized_agents, prefix="unauthorized"
        )
        authorized_agents_formset = AgentFormSet(queryset=authorized_agents, prefix="authorized")

    context = {
        "unauthorized_agents_formset": unauthorized_agents_formset,
        "authorized_agents_formset": authorized_agents_formset,
        "btn_submit": {
            "label": "Enregistrer",
            "type": "submit",
            "disabled": True,
        },
    }

    return render(request, "agent_admin/manage_access.html", context)
