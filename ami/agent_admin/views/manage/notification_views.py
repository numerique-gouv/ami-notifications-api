import json

from django.contrib import messages
from django.shortcuts import render

from ami.agent.decorators import (
    agent_login_required,
    role_notifications_required,
)
from ami.agent_admin.forms import NotificationForm


@agent_login_required
@role_notifications_required
def send_notification(request):
    if request.method == "POST":
        form = NotificationForm(data=request.POST)
        if form.is_valid():
            message_content = form.submit()
            message = {
                "title": "Notification envoyée avec succès",
                "content": message_content,
            }
            messages.success(request, json.dumps(message))
    else:
        form = NotificationForm()
    context = {
        "form": form,
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
    }
    return render(request, "agent_admin/manage/send_notification.html", context)
