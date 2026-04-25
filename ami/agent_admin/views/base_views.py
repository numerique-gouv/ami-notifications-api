from django.shortcuts import render
from django.urls import reverse

from ami.agent.decorators import (
    agent_login_required,
    role_support_required,
)


@agent_login_required
@role_support_required
def home(request):
    return render(request, "agent_admin/home.html", {})


def login(request):
    return render(request, "agent_admin/login.html", {})


@agent_login_required
def access_denied(request):
    home_url = reverse("agent-admin:home")
    context = {
        "btn_group": {
            "items": [
                {
                    "label": "Recharger",
                    "type": "button",
                    "extra_classes": "fr-btn--secondary",
                    "onclick": f"window.location.href = '{home_url}';",
                },
            ],
            "extra_classes": "fr-btns-group--inline fr-btns-group--form-actions",
        },
    }
    return render(request, "agent_admin/access_denied.html", context)
