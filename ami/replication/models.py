from __future__ import annotations

import hashlib
import uuid

from django.db import models
from django.utils import timezone

from ami.notification.models import Notification
from ami.user.models import Registration, User


class AnonymizedModel(models.Model):
    # The anonymized classes are like the original ones, to the exception of :
    # * We have not included fields that could identify individuals
    # * The auto-added options of certains date fields have been removed to replicate the value from the original object
    # * An id has been added

    replication_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True

    @classmethod
    def from_source(cls, source):
        defaults = {
            field.name: getattr(source, field.name)
            for field in cls._meta.concrete_fields
            if not field.primary_key and field.name != "id"
        }
        instance, _ = cls.objects.update_or_create(
            id=source.id,
            defaults=defaults,
        )
        return instance


class AnonymizedNotification(AnonymizedModel):
    id = models.UUIDField(editable=False)

    user_id = models.UUIDField(null=True, db_index=True)

    content_title = models.CharField()
    content_body = models.CharField()
    # No `content_private_body` here.
    content_subheading = models.CharField(blank=True, null=True)
    content_icon = models.CharField(blank=True, null=True)
    content_link = models.CharField(blank=True, null=True)

    item_type = models.CharField(blank=True, null=True)
    item_id = models.CharField(blank=True, null=True)
    item_parent_partner_id = models.CharField(blank=True, null=True)
    item_parent_type = models.CharField(blank=True, null=True)
    item_parent_id = models.CharField(blank=True, null=True)
    item_status_label = models.CharField(blank=True, null=True)
    item_generic_status = models.CharField(blank=True, null=True)
    item_canal = models.CharField(blank=True, null=True)
    item_milestone_start_date = models.DateTimeField(blank=True, null=True)
    item_milestone_end_date = models.DateTimeField(blank=True, null=True)

    send_status = models.BooleanField(blank=True, null=True)
    partner_id = models.CharField()
    internal_url = models.CharField(blank=True, null=True)

    read = models.BooleanField(default=False)
    event_date = models.DateTimeField(default=timezone.now)
    try_push = models.BooleanField(blank=True, null=True)

    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta(AnonymizedModel.Meta):
        db_table = "ami_notification_anonymized"

    @classmethod
    def from_notification(cls, notification: Notification) -> AnonymizedNotification:
        return cls.from_source(notification)


class AnonymizedUser(AnonymizedModel):
    # Fields synchronized from original class
    id = models.UUIDField(editable=False)
    last_logged_in = models.DateTimeField(blank=True, null=True)
    consent_datetime = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta(AnonymizedModel.Meta):
        db_table = "ami_user_anonymized"

    @classmethod
    def from_user(cls, user: User) -> AnonymizedUser:
        return cls.from_source(user)


class AnonymizedRegistration(AnonymizedModel):
    id = models.UUIDField(editable=False)

    user_id = models.UUIDField(null=True, db_index=True)

    subscription = models.JSONField(blank=True, null=True)

    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta(AnonymizedModel.Meta):
        db_table = "ami_registration_anonymized"

    @staticmethod
    def _is_mobile_subscription(subscription: dict) -> bool:
        return "app_version" in subscription

    @classmethod
    def from_source(cls, source):
        defaults = {
            field.name: getattr(source, field.name)
            for field in cls._meta.concrete_fields
            if not field.primary_key and field.name != "id"
        }
        if defaults.get("subscription"):
            sub = dict(defaults["subscription"])
            if cls._is_mobile_subscription(sub):
                for field in ("device_id", "fcm_token"):
                    if field in sub:
                        sub[field] = hashlib.sha256(sub[field].encode()).hexdigest()
            else:
                sub = dict()
            defaults["subscription"] = sub
        instance, _ = cls.objects.update_or_create(
            id=source.id,
            defaults=defaults,
        )
        return instance

    @classmethod
    def from_registration(cls, registration: Registration) -> AnonymizedRegistration:
        return cls.from_source(registration)
