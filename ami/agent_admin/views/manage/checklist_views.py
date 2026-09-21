from django.contrib import messages
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from ami.agent.decorators import (
    agent_login_required,
    role_admin_required,
)
from ami.agent_admin.forms import CheckListForm
from ami.agent_admin.utils import audit
from ami.checklist.models import CheckList


@agent_login_required
@role_admin_required
def list_checklists(request):
    context = {
        "object_list": CheckList.objects.all().order_by("external_id"),
        "btn_group": {
            "items": [
                {
                    "label": "Ajouter une liste d’étapes",
                    "type": "button",
                    "onclick": f"window.location.href = '{reverse('agent-admin:manage:add-checklist')}';",
                },
            ],
            "extra_classes": "fr-btns-group--inline fr-btns-group--form-actions",
        },
    }
    return render(request, "agent_admin/manage/list_checklists.html", context)


def add_edit_checklist(checklist: CheckList | None, request, for_update=True):
    if request.method == "POST":
        form = CheckListForm(data=request.POST, instance=checklist, author=request.user.agent)
        if form.is_valid():
            with transaction.atomic():
                form.save()
            if for_update:
                messages.success(request, "La liste d’étapes a bien été modifiée.")
            else:
                messages.success(request, "La liste d’étapes a bien été ajoutée.")
            return redirect(reverse("agent-admin:manage:list-checklists"))
    else:
        form = CheckListForm(instance=checklist, author=request.user.agent)
    buttons = [
        {
            "label": "Annuler",
            "type": "button",
            "extra_classes": "fr-btn--secondary",
            "onclick": f"window.location.href = '{reverse('agent-admin:manage:list-checklists')}';",
        },
    ]
    if for_update:
        buttons.append(
            {
                "label": "Supprimer",
                "type": "button",
                "extra_classes": "fr-btn--secondary",
                "onclick": "confirmModal('modal-delete-checklist');",
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
        "instance": checklist,
        "form": form,
        "btn_group": {
            "items": buttons,
            "extra_classes": "fr-btns-group--inline fr-btns-group--form-actions",
        },
    }
    return render(request, "agent_admin/manage/add_edit_checklist.html", context)


@agent_login_required
@role_admin_required
def add_checklist(request):
    checklist = CheckList()
    return add_edit_checklist(checklist, request, for_update=False)


@agent_login_required
@role_admin_required
def edit_checklist(request, checklist_id):
    checklist = get_object_or_404(CheckList, id=checklist_id)
    return add_edit_checklist(checklist, request)


@agent_login_required
@role_admin_required
@require_http_methods(["POST"])
@csrf_exempt
def delete_checklist(request, checklist_id):
    checklist = get_object_or_404(CheckList, id=checklist_id)
    with transaction.atomic():
        audit("checklists:checklist-removed", request.user.agent, {"checklist": checklist})
        checklist.delete()

    messages.success(request, "La liste d’étapes a bien été supprimée.")
    return redirect(reverse("agent-admin:manage:list-checklists"))
