from django.contrib import messages
from django.db import transaction
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from ami.agent.decorators import (
    agent_login_required,
    role_admin_required,
)
from ami.agent_admin.forms import ServiceForm
from ami.agent_admin.utils import audit
from ami.service.models import Service


@agent_login_required
@role_admin_required
def list_services(request):
    context = {
        "catalog_object_list": Service.objects.filter(kind=Service.Kind.CATALOG).order_by("title"),
        "sos_object_list": Service.objects.filter(kind=Service.Kind.SOS).order_by("title"),
        "steps_object_list": Service.objects.filter(kind=Service.Kind.STEPS).order_by("title"),
        "catalog_btn_group": {
            "items": [
                {
                    "label": "Ajouter une démarche dans le catalogue",
                    "type": "button",
                    "onclick": f"window.location.href = '{reverse('agent-admin:manage:add-service', args=[Service.Kind.CATALOG])}';",
                },
            ],
            "extra_classes": "fr-btns-group--inline fr-btns-group--form-actions",
        },
        "sos_btn_group": {
            "items": [
                {
                    "label": "Ajouter une démarche dans la section « SOS »",
                    "type": "button",
                    "onclick": f"window.location.href = '{reverse('agent-admin:manage:add-service', args=[Service.Kind.SOS])}';",
                },
            ],
            "extra_classes": "fr-btns-group--inline fr-btns-group--form-actions",
        },
        "steps_btn_group": {
            "items": [
                {
                    "label": "Ajouter une démarche dans la section « Comment faire »",
                    "type": "button",
                    "onclick": f"window.location.href = '{reverse('agent-admin:manage:add-service', args=[Service.Kind.STEPS])}';",
                },
            ],
            "extra_classes": "fr-btns-group--inline fr-btns-group--form-actions",
        },
    }
    return render(request, "agent_admin/manage/list_services.html", context)


def add_edit_service(service: Service | None, request, for_update=True):
    if request.method == "POST":
        form = ServiceForm(data=request.POST, instance=service, author=request.user.agent)
        if form.is_valid():
            with transaction.atomic():
                form.save()
            if for_update:
                messages.success(request, "La démarche a bien été modifiée.")
            else:
                messages.success(request, "La démarche a bien été ajoutée.")
            return redirect(reverse("agent-admin:manage:list-services"))
    else:
        form = ServiceForm(instance=service, author=request.user.agent)
    buttons = [
        {
            "label": "Annuler",
            "type": "button",
            "extra_classes": "fr-btn--secondary",
            "onclick": f"window.location.href = '{reverse('agent-admin:manage:list-services')}';",
        },
    ]
    if for_update:
        buttons.append(
            {
                "label": "Supprimer",
                "type": "button",
                "extra_classes": "fr-btn--secondary",
                "onclick": "confirmModal('modal-delete-service');",
            }
        )
    buttons.append(
        {
            "label": "Enregistrer",
            "type": "submit",
        }
    )
    context = {
        "for_update": for_update,
        "instance": service,
        "form": form,
        "btn_group": {
            "items": buttons,
            "extra_classes": "fr-btns-group--inline fr-btns-group--form-actions",
        },
    }
    return render(request, "agent_admin/manage/add_edit_service.html", context)


@agent_login_required
@role_admin_required
def add_service(request, kind):
    if kind not in Service.Kind:
        raise Http404
    service = Service(kind=kind)
    return add_edit_service(service, request, for_update=False)


@agent_login_required
@role_admin_required
def edit_service(request, service_id):
    service = get_object_or_404(Service, id=service_id)
    return add_edit_service(service, request)


@agent_login_required
@role_admin_required
@require_http_methods(["POST"])
@csrf_exempt
def delete_service(request, service_id):
    service = get_object_or_404(Service, id=service_id)
    with transaction.atomic():
        audit("services:service-removed", request.user.agent, {"service": service})
        service.delete()

    messages.success(request, "La démarche a bien été supprimée.")
    return redirect(reverse("agent-admin:manage:list-services"))
