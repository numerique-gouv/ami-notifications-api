import markdown
import nh3
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
from ami.agent_admin.forms import PageForm, SectionForm
from ami.agent_admin.utils import audit
from ami.page.models import Page, Section


@agent_login_required
@role_admin_required
def list_pages(request):
    context = {
        "object_list": Page.objects.all().order_by("title"),
        "btn_group": {
            "items": [
                {
                    "label": "Ajouter une page",
                    "type": "button",
                    "onclick": f"window.location.href = '{reverse('agent-admin:manage:add-page')}';",
                },
            ],
            "extra_classes": "fr-btns-group--inline fr-btns-group--form-actions",
        },
    }
    return render(request, "agent_admin/manage/list_pages.html", context)


def add_edit_page(page: Page, request, for_update=True):
    if request.method == "POST":
        form = PageForm(data=request.POST, instance=page, author=request.user.agent)
        if form.is_valid():
            with transaction.atomic():
                form.save()
            if for_update:
                messages.success(request, "La page a bien été modifiée.")
                return redirect(reverse("agent-admin:manage:list-pages"))
            else:
                messages.success(request, "La page a bien été ajoutée.")
                return redirect(
                    reverse("agent-admin:manage:edit-page", kwargs={"page_id": page.id})
                )
    else:
        form = PageForm(instance=page, author=request.user.agent)
    buttons = [
        {
            "label": "Annuler",
            "type": "button",
            "extra_classes": "fr-btn--secondary",
            "onclick": f"window.location.href = '{reverse('agent-admin:manage:list-pages')}';",
        },
    ]
    if for_update:
        buttons.append(
            {
                "label": "Supprimer",
                "type": "button",
                "extra_classes": "fr-btn--secondary",
                "onclick": "confirmModal('modal-delete-page');",
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
        "instance": page,
        "form": form,
        "btn_group": {
            "items": buttons,
            "extra_classes": "fr-btns-group--inline fr-btns-group--form-actions",
        },
    }
    if for_update:
        context["sections_btn_group"] = {
            "items": [
                {
                    "label": "Ajouter une section",
                    "type": "button",
                    "onclick": f"window.location.href = '{reverse('agent-admin:manage:add-section', kwargs={'page_id': page.id})}';",
                },
            ],
            "extra_classes": "fr-btns-group--inline fr-btns-group--form-actions",
        }

    return render(request, "agent_admin/manage/add_edit_page.html", context)


@agent_login_required
@role_admin_required
def add_page(request):
    page = Page()
    return add_edit_page(page, request, for_update=False)


@agent_login_required
@role_admin_required
def edit_page(request, page_id):
    page = get_object_or_404(Page, id=page_id)
    return add_edit_page(page, request)


@agent_login_required
@role_admin_required
@require_http_methods(["POST"])
@csrf_exempt
def delete_page(request, page_id):
    page = get_object_or_404(Page, id=page_id)
    with transaction.atomic():
        audit("pages:page-removed", request.user.agent, {"page": page})
        page.delete()

    messages.success(request, "La page a bien été supprimée.")
    return redirect(reverse("agent-admin:manage:list-pages"))


def add_edit_section(section: Section, request, for_update=True):
    if request.method == "POST":
        form = SectionForm(data=request.POST, instance=section, author=request.user.agent)
        if form.is_valid():
            with transaction.atomic():
                form.save()
            if for_update:
                messages.success(request, "La section a bien été modifiée.")
            else:
                messages.success(request, "La section a bien été ajoutée.")
            if request.POST.get("save-and-continue"):
                return redirect(
                    reverse(
                        "agent-admin:manage:edit-section",
                        kwargs={"page_id": section.page.id, "section_id": section.id},
                    )
                )
            else:
                return redirect(
                    reverse("agent-admin:manage:edit-page", kwargs={"page_id": section.page.id})
                )
    else:
        form = SectionForm(instance=section, author=request.user.agent)
    buttons = [
        {
            "label": "Annuler",
            "type": "button",
            "extra_classes": "fr-btn--secondary",
            "onclick": f"window.location.href = '{reverse('agent-admin:manage:edit-page', kwargs={'page_id': section.page.id})}';",
        },
    ]
    if for_update:
        buttons.append(
            {
                "label": "Supprimer",
                "type": "button",
                "extra_classes": "fr-btn--secondary",
                "onclick": "confirmModal('modal-delete-section');",
            }
        )
    buttons.extend(
        [
            {
                "label": "Enregistrer et continuer",
                "name": "save-and-continue",
                "type": "button",
                "onclick": "save_and_continue()",
            },
            {
                "label": "Enregistrer",
                "type": "submit",
            },
        ]
    )
    try:
        preview = nh3.clean(markdown.markdown(section.text or ""))
    except Exception as e:
        preview = f"Erreur de rendu ({e})"
    context = {
        "for_update": for_update,
        "instance": section,
        "form": form,
        "btn_group": {
            "items": buttons,
            "extra_classes": "fr-btns-group--inline fr-btns-group--form-actions",
        },
        "preview": preview,
    }
    return render(request, "agent_admin/manage/add_edit_section.html", context)


@agent_login_required
@role_admin_required
def add_section(request, page_id):
    section = Section()
    section.page = Page.objects.get(id=page_id)
    return add_edit_section(section, request, for_update=False)


@agent_login_required
@role_admin_required
def edit_section(request, page_id, section_id):
    section = get_object_or_404(Section, id=section_id, page_id=page_id)
    return add_edit_section(section, request)


@agent_login_required
@role_admin_required
@require_http_methods(["POST"])
@csrf_exempt
def delete_section(request, page_id, section_id):
    section = get_object_or_404(Section, id=section_id, page_id=page_id)
    with transaction.atomic():
        audit("pages:section-removed", request.user.agent, {"section": section})
        section.delete()

    messages.success(request, "La section a bien été supprimée.")
    return redirect(reverse("agent-admin:manage:edit-page", kwargs={"page_id": section.page.id}))
