from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.timezone import now

from ami.agent.decorators import agent_login_required, role_admin_required, role_support_required
from ami.agent.models import Agent
from ami.agent_admin.forms import AgentFormSet
from ami.agent_admin.models import RolesRecordEntry


@agent_login_required
@role_support_required
def home(request):
    return render(request, "agent_admin/home.html", {"user": request.user})


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
    roles_record = RolesRecordEntry.objects.all()

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
            update_roles_record(request, authorized_agents_formset, unauthorized_agents_formset)
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
        "roles_record": roles_record,
    }

    return render(request, "agent_admin/manage_access.html", context)


def update_roles_record(request, authorized_agents_formset, unauthorized_agents_formset):
    admin_agent = Agent.objects.get(user=request.user)
    for form in authorized_agents_formset:
        if form.has_changed():
            create_roles_record_entry(admin_agent, form)
    for form in unauthorized_agents_formset:
        if form.has_changed():
            create_roles_record_entry(admin_agent, form)


def create_roles_record_entry(admin_agent, form):
    updated_agent = form.instance
    new_role = form.cleaned_data["role"]
    updated_user_from_db = Agent.objects.get(id=form.instance.id)
    old_role = updated_user_from_db.role
    update_date = now()
    RolesRecordEntry.objects.create(
        updated_agent=updated_agent,
        admin_agent=admin_agent,
        new_role=new_role,
        old_role=old_role,
        update_date=update_date,
    )
