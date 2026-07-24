from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from ami.agent.decorators import (
    agent_login_required,
    role_admin_required,
)
from ami.agent_admin.forms import ServiceForm
from ami.service.models import Service


@agent_login_required
@role_admin_required
def list_services(request):
    context = {
        "object_list": Service.objects.all().order_by("title"),
        "btn_group": {
            "items": [
                {
                    "label": "Ajouter une démarche",
                    "type": "button",
                    "onclick": f"window.location.href = '{reverse('agent-admin:manage:add-service')}';",
                },
            ],
            "extra_classes": "fr-btns-group--inline fr-btns-group--form-actions",
        },
    }
    return render(request, "agent_admin/manage/list_services.html", context)


def add_edit_service(service: Service | None, request):
    if request.method == "POST":
        form = ServiceForm(data=request.POST, instance=service)
        if form.is_valid():
            form.save()
            if service is not None:
                messages.success(request, "La démarche a bien été modifiée.")
            else:
                messages.success(request, "La démarche a bien été ajoutée.")
            return redirect(reverse("agent-admin:manage:list-services"))
    else:
        form = ServiceForm(instance=service)
    context = {
        "instance": service,
        "form": form,
        "btn_group": {
            "items": [
                {
                    "label": "Annuler",
                    "type": "button",
                    "extra_classes": "fr-btn--secondary",
                    "onclick": f"window.location.href = '{reverse('agent-admin:manage:list-services')}';",
                },
                {
                    "label": "Enregistrer",
                    "type": "submit",
                },
            ],
            "extra_classes": "fr-btns-group--inline fr-btns-group--form-actions",
        },
    }
    return render(request, "agent_admin/manage/add_edit_service.html", context)


@agent_login_required
@role_admin_required
def add_service(request):
    return add_edit_service(None, request)


@agent_login_required
@role_admin_required
def edit_service(request, service_id):
    service = get_object_or_404(Service, id=service_id)
    return add_edit_service(service, request)
