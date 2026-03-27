import uuid

from django.db import models

from ami.agent.models import Agent


class RolesRecordEntry(models.Model):
    class Role(models.TextChoices):
        SUPPORT = "support", "Support"
        NOTIFICATIONS = "notifications", "Notifications"
        ADMIN = "admin", "Admin"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    updated_agent = models.ForeignKey(
        Agent,
        on_delete=models.CASCADE,
        related_name="roles_as_updated_agent",
    )
    admin_agent = models.ForeignKey(
        Agent,
        on_delete=models.CASCADE,
        related_name="roles_as_admin_agent",
    )
    new_role = models.CharField(
        max_length=20,
        choices=Role,
        null=True,
        blank=True,
    )
    old_role = models.CharField(
        max_length=20,
        choices=Role,
        null=True,
        blank=True,
    )
    update_date = models.DateTimeField(null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
