import uuid

from django.db import models

from ami.agent.models import Agent


class AuditEntry(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    author = models.ForeignKey(Agent, on_delete=models.SET_NULL, null=True)
    author_first_name = models.CharField(max_length=150)
    author_last_name = models.CharField(max_length=150)
    author_email = models.EmailField()
    author_proconnect_sub = models.CharField(max_length=255)

    action_type = models.CharField(max_length=100, db_index=True)
    action_code = models.CharField(max_length=100, db_index=True)
    extra_data = models.JSONField(blank=True, default=dict)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    @property
    def author_name(self):
        if self.author:
            full_name = f"{self.author.user.last_name} {self.author.user.first_name}"
        full_name = f"{self.author_last_name} {self.author_first_name}"
        return full_name.strip()

    @property
    def agent_name(self):
        last_name = self.extra_data.get("agent_last_name") or ""
        first_name = self.extra_data.get("agent_first_name") or ""
        full_name = f"{last_name} {first_name}"
        return full_name.strip()
