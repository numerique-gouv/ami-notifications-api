import uuid

from django.contrib.auth.models import User
from django.db import models


class Agent(models.Model):
    class Role(models.TextChoices):
        __empty__ = "Aucun"
        SUPPORT = "support", "Support"
        NOTIFICATIONS = "notifications", "Notifications"
        ADMIN = "admin", "Admin"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    proconnect_sub = models.CharField(max_length=255, unique=True)
    role = models.CharField(
        max_length=20,
        choices=Role,
        null=True,
        blank=True,
    )
    proconnect_last_login = models.DateTimeField(null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} ({self.user.email})"

    @property
    def has_role_support(self):
        return self.role is not None

    @property
    def has_role_notifications(self):
        return self.role in [Agent.Role.SUPPORT, Agent.Role.NOTIFICATIONS]

    @property
    def has_role_admin(self):
        return self.role == Agent.Role.ADMIN
