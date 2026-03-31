from django import forms
from dsfr.forms import DsfrBaseForm

from ami.agent.models import Agent
from ami.agent_admin.utils import audit


class AgentForm(forms.ModelForm, DsfrBaseForm):
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
