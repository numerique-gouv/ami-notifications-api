from django.contrib import messages
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from ami.agent.decorators import (
    agent_login_required,
    role_admin_required,
)
from ami.agent_admin.forms import PartnerForm
from ami.partner.models import Partner


@agent_login_required
@role_admin_required
def list_partners(request):
    context = {
        "object_list": Partner.objects.all().order_by("name"),
        "btn_group": {
            "items": [
                {
                    "label": "Ajouter un partenaire",
                    "type": "button",
                    "onclick": f"window.location.href = '{reverse('agent-admin:manage:add-partner')}';",
                },
            ],
            "extra_classes": "fr-btns-group--inline fr-btns-group--form-actions",
        },
    }
    return render(request, "agent_admin/manage/list_partners.html", context)


def add_edit_partner(partner: Partner | None, request, for_update=True):
    if request.method == "POST":
        form = PartnerForm(data=request.POST, instance=partner, author=request.user.agent)
        if form.is_valid():
            with transaction.atomic():
                form.save()
            if for_update:
                messages.success(request, "Le partenaire a bien été modifié.")
            else:
                messages.success(request, "Le partenaire a bien été ajouté.")
            return redirect(reverse("agent-admin:manage:list-partners"))
    else:
        form = PartnerForm(instance=partner, author=request.user.agent)
    buttons = [
        {
            "label": "Annuler",
            "type": "button",
            "extra_classes": "fr-btn--secondary",
            "onclick": f"window.location.href = '{reverse('agent-admin:manage:list-partners')}';",
        },
        {
            "label": "Enregistrer",
            "type": "submit",
        },
    ]
    context = {
        "for_update": for_update,
        "instance": partner,
        "form": form,
        "btn_group": {
            "items": buttons,
            "extra_classes": "fr-btns-group--inline fr-btns-group--form-actions",
        },
    }
    return render(request, "agent_admin/manage/add_edit_partner.html", context)


@agent_login_required
@role_admin_required
def add_partner(request):
    partner = Partner()
    return add_edit_partner(partner, request, for_update=False)


@agent_login_required
@role_admin_required
def edit_partner(request, partner_id):
    partner = get_object_or_404(Partner, id=partner_id)
    return add_edit_partner(partner, request)
