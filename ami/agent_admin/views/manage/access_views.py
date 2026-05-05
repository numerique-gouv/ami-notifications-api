from django.db import transaction
from django.shortcuts import redirect, render
from django.urls import reverse

from ami.agent.decorators import (
    agent_login_required,
    role_admin_required,
)
from ami.agent.models import Agent
from ami.agent_admin.forms import AgentFormSet
from ami.agent_admin.models import AuditEntry


@agent_login_required
@role_admin_required
def access(request):
    unauthorized_agents = Agent.objects.filter(role__isnull=True).order_by("-proconnect_last_login")
    authorized_agents = Agent.objects.filter(role__isnull=False).order_by(
        "user__last_name",
        "user__first_name",
    )

    if request.method == "POST":
        unauthorized_agents_formset = AgentFormSet(
            request.POST,
            queryset=unauthorized_agents,
            prefix="unauthorized",
            form_kwargs={"author": request.user.agent},
        )
        authorized_agents_formset = AgentFormSet(
            request.POST,
            queryset=authorized_agents,
            prefix="authorized",
            form_kwargs={"author": request.user.agent},
        )
        is_unauthorized_agents_formset_valid = unauthorized_agents_formset.is_valid()
        is_authorized_agents_formset_valid = authorized_agents_formset.is_valid()
        if is_unauthorized_agents_formset_valid and is_authorized_agents_formset_valid:
            with transaction.atomic():
                unauthorized_agents_formset.save()
                authorized_agents_formset.save()
            return redirect(reverse("agent-admin:manage:access"))
    else:
        unauthorized_agents_formset = AgentFormSet(
            queryset=unauthorized_agents,
            prefix="unauthorized",
            form_kwargs={"author": request.user.agent},
        )
        authorized_agents_formset = AgentFormSet(
            queryset=authorized_agents,
            prefix="authorized",
            form_kwargs={"author": request.user.agent},
        )

    context = {
        "unauthorized_agents_formset": unauthorized_agents_formset,
        "authorized_agents_formset": authorized_agents_formset,
        "btn_group": {
            "items": [
                {
                    "label": "Annuler",
                    "type": "button",
                    "extra_classes": "fr-btn--secondary",
                    "onclick": "window.location.href = window.location.href;",
                },
                {
                    "label": "Enregistrer",
                    "type": "submit",
                },
            ],
            "extra_classes": "fr-btns-group--inline fr-btns-group--form-actions",
        },
        "aes": AuditEntry.objects.filter(
            action_type="access",
            action_code__in=["role-added", "role-updated", "role-removed"],
        ),
    }

    return render(request, "agent_admin/manage/list_access.html", context)
