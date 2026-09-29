import uuid

from django.db import models
from pydantic import BaseModel
from webpush import WebPushSubscription

from ami.partner.models import Partner


class User(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    fc_hash = models.CharField(unique=True)
    last_logged_in = models.DateTimeField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "ami_user"


class Consent(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.ForeignKey(User, on_delete=models.PROTECT)
    partner = models.ForeignKey(
        Partner, models.PROTECT, db_column="partner_uuid", related_name="consents"
    )
    consent_datetime = models.DateTimeField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # to delete from DB in a future release
    # partner_slug = models.CharField(max_length=100, db_column="partner_id", null=True)

    class Meta:
        db_table = "consent"
        unique_together = [("user", "partner")]


class PersonalDataConsent(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.OneToOneField(User, on_delete=models.PROTECT)
    consent_datetime = models.DateTimeField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "personal_data_consent"


class MobileAppSubscription(BaseModel):
    app_version: str
    device_id: str
    fcm_token: str
    model: str
    platform: str


class NotDeletedManager(models.Manager):
    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(deleted_at__isnull=True)


class Registration(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.ForeignKey(User, on_delete=models.PROTECT)

    device_id = models.CharField(blank=True, null=True)

    subscription = models.JSONField(blank=True, null=True)

    deleted_at = models.DateTimeField(null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = NotDeletedManager()
    all_objects = models.Manager()

    @property
    def typed_subscription(self) -> WebPushSubscription | MobileAppSubscription:
        """Convert the stored dict to the proper subscription type."""
        try:
            return WebPushSubscription.model_validate(self.subscription)
        except Exception:
            return MobileAppSubscription.model_validate(self.subscription)

    class Meta:
        db_table = "registration"


class NotificationPush(BaseModel):
    title: str
    message: str
    content_icon: str | None
    sender: str
