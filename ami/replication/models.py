from __future__ import annotations

import uuid

from django.db import models

from ami.user.models import User


class AnonymizedUser(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    original_id = models.UUIDField(unique=True)

    last_logged_in = models.DateTimeField(blank=True, null=True)

    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        db_table = "ami_user_anonymized"

    @classmethod
    def from_user(cls, user: User, using: str = "default") -> AnonymizedUser:
        instance, _ = cls.objects.using(using).update_or_create(
            original_id=user.id,
            defaults={
                "last_logged_in": user.last_logged_in,
                "created_at": user.created_at,
                "updated_at": user.updated_at,
            },
        )
        return instance
