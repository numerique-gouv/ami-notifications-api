from __future__ import annotations

import uuid

from django.db import models

from ami.user.models import User

"""
The anonymized classes are like the original ones, to the exception of :
* We have not included fields that could identify individuals
* The auto-added options of certains date fields have been removed to replicate the value from the original object
* An id has been added
"""


class AnonymizedModel(models.Model):
    class Meta:
        abstract = True

    @classmethod
    def from_source(cls, source, using: str = "default"):
        defaults = {
            field.name: getattr(source, field.name)
            for field in cls._meta.concrete_fields
            if not field.primary_key and field.name != "replication_id" and field.name != "id"
        }
        instance, _ = cls.objects.using(using).update_or_create(
            id=source.id,
            defaults=defaults,
        )
        return instance


class AnonymizedUser(AnonymizedModel):
    # New Field - name must match the given one in the method from_source
    replication_id = models.UUIDField(primary_key=True, default=uuid.uuid4)

    # Fields synchronized from original class
    id = models.UUIDField(editable=False)
    last_logged_in = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta(AnonymizedModel.Meta):
        db_table = "ami_user_anonymized"

    @classmethod
    def from_user(cls, user: User, using: str = "default") -> AnonymizedUser:
        return cls.from_source(user, using)
