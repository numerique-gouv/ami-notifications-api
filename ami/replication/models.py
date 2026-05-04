from __future__ import annotations

import uuid

from django.db import models
from django.utils import timezone

from ami.notification.models import Notification
from ami.user.models import Registration, User

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


class AnonymizedNotification(AnonymizedModel):
    # New Field - name must match the given one in the method from_source
    replication_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Not specifiying user reference

    id = models.UUIDField(editable=False)
    content_title = models.CharField()
    content_body = models.CharField()
    content_icon = models.CharField(blank=True, null=True)

    item_type = models.CharField(blank=True, null=True)
    item_id = models.CharField(blank=True, null=True)
    item_status_label = models.CharField(blank=True, null=True)
    item_generic_status = models.CharField(blank=True, null=True)
    item_canal = models.CharField(blank=True, null=True)
    item_milestone_start_date = models.DateTimeField(blank=True, null=True)
    item_milestone_end_date = models.DateTimeField(blank=True, null=True)
    item_external_url = models.CharField(blank=True, null=True)

    send_status = models.BooleanField(blank=True, null=True)
    partner_id = models.CharField()
    internal_url = models.CharField(
        blank=True, null=True
    )  # to link notification to a front url; used by scheduled notifications

    read = models.BooleanField(default=False)
    send_date = models.DateTimeField(default=timezone.now)
    try_push = models.BooleanField(blank=True, null=True)

    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta(AnonymizedModel.Meta):
        db_table = "ami_notification_anonymized"

    @classmethod
    def from_notification(
        cls, notification: Notification, using: str = "default"
    ) -> AnonymizedNotification:
        return cls.from_source(notification, using)


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


class AnonymizedRegistration(AnonymizedModel):
    # New Field - name must match the given one in the method from_source
    replication_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Not specifying user reference nor subscription data
    id = models.UUIDField(editable=False)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta(AnonymizedModel.Meta):
        db_table = "ami_registration_anonymized"

    @classmethod
    def from_registration(
        cls, registration: Registration, using: str = "default"
    ) -> AnonymizedRegistration:
        return cls.from_source(registration, using)
