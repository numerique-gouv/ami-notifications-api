import json

from django import forms
from django.conf import settings
from django.urls import reverse
from django.utils.timezone import now
from rest_framework.renderers import JSONRenderer

from ami.agent.models import Agent
from ami.agent_admin.utils import audit
from ami.amidsfr.forms import AMIDsfrBaseForm
from ami.amidsfr.widgets import AutocompleteInput, ToggleInput
from ami.partner.models import partners
from ami.utils.httpx import BasicAuth, httpxLaxClient


class AgentForm(forms.ModelForm, AMIDsfrBaseForm):
    class Meta:
        model = Agent
        fields = ["role"]

    def __init__(self, *args, **kwargs):
        self.author = kwargs.pop("author")
        super().__init__(*args, **kwargs)
        self.old_role = self.instance.role

    def save(self, commit=True):
        super().save(commit=commit)
        new_role = self.instance.role

        if self.old_role is None:
            action = "access:role-added"
            extra_data = {"agent": self.instance, "new_role": new_role}
        elif new_role is None:
            action = "access:role-removed"
            extra_data = {"agent": self.instance, "old_role": self.old_role}
        else:
            action = "access:role-updated"
            extra_data = {"agent": self.instance, "new_role": new_role, "old_role": self.old_role}
        audit(action, self.author, extra_data)

        return self.instance


AgentFormSet = forms.modelformset_factory(Agent, extra=0, form=AgentForm)


class NotificationForm(AMIDsfrBaseForm):
    recipient_fc_hash = forms.CharField()

    content_title = forms.CharField()
    content_body = forms.CharField(
        widget=forms.Textarea(attrs={"rows": 4}),
    )
    content_icon = forms.CharField(
        required=False,
    )

    item_type = forms.CharField(
        required=False,
    )
    item_id = forms.CharField(
        required=False,
    )
    item_status_label = forms.CharField(
        required=False,
    )
    item_generic_status = forms.ChoiceField(
        required=False,
        choices=[("", "--------"), ("new", "new"), ("wip", "wip"), ("closed", "closed")],
        initial="new",
    )
    item_canal = forms.CharField(
        required=False,
        initial="admin",
    )
    item_milestone_start_date = forms.DateTimeField(
        required=False,
        widget=forms.DateTimeInput(attrs={"type": "datetime-local"}),
    )
    item_milestone_end_date = forms.DateTimeField(
        required=False,
        widget=forms.DateTimeInput(attrs={"type": "datetime-local"}),
    )
    item_external_url = forms.CharField(
        required=False,
    )

    send_date = forms.DateTimeField(
        initial=now,
        widget=forms.DateTimeInput(
            attrs={"type": "datetime-local"}, format="%Y-%m-%dT%H:%M:00.000%Z"
        ),
    )
    try_push = forms.BooleanField(
        required=False,
        initial=False,
        widget=ToggleInput,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["recipient_fc_hash"].widget = AutocompleteInput(
            autocomplete_url=reverse("agent-admin:api-users")
        )

    def submit(self):
        payload = json.loads(JSONRenderer().render(self.cleaned_data))
        # remove empty values
        payload = {k: v for k, v in payload.items() if v not in ["", None]}

        # send notification as AMI partner
        partner = partners["dinum-ami"]

        auth = BasicAuth(username=partner.id, password=partner.secret)
        with httpxLaxClient() as httpx_client:
            response = httpx_client.post(
                f"{settings.PUBLIC_API_URL}/api/v1/notifications",
                auth=auth,
                json=payload,
            )

        if response.status_code == 404:
            try:
                self.add_error(None, response.json()["error"])
            except (KeyError, json.JSONDecodeError):
                self.add_error(None, "Not found error")
            return

        if response.status_code // 100 == 4:
            # notification request error
            for key, values in response.json().items():
                for value in values:
                    if key in self.fields:
                        self.add_error(key, value)
                    else:
                        self.add_error(None, value)
            return

        if response.status_code // 100 == 2:
            # notification request accepted
            return {
                "title": "Notification envoyée avec succès",
                "type": "success",
                "content": json.dumps(response.json()),
                "is_collapsible": True,
                "id": "alert-success-tag",
            }
