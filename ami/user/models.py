import uuid

from django.db import models
from pydantic import BaseModel
from webpush import WebPushSubscription


class User(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    sa_orm_sentinel = models.IntegerField(blank=True, null=True)
    fc_hash = models.CharField(unique=True)
    last_logged_in = models.DateTimeField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "ami_user"


class MobileAppSubscription(BaseModel):
    app_version: str
    device_id: str
    fcm_token: str
    model: str
    platform: str


class Registration(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    subscription = models.JSONField(blank=True, null=True)
    sa_orm_sentinel = models.IntegerField(blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.PROTECT)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

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
