import uuid
from enum import Enum

from asgiref.sync import async_to_sync
from django.db import models
from django.utils import timezone

from ami.user.models import User


class NotificationEvent(str, Enum):  # Subclassing `str` makes it automagically serializable in json
    CREATED = "created"
    UPDATED = "updated"
    DELETED = "deleted"


class Notification(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user_id: uuid.UUID  # For typing purposes: this is only a type annotation
    user = models.ForeignKey(User, models.PROTECT)

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

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "notification"

    @property
    def url(self):
        return self.item_external_url or self.internal_url


class ScheduledNotification(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.ForeignKey(User, models.PROTECT)
    reference = models.CharField()

    content_title = models.CharField()
    content_body = models.CharField()
    content_icon = models.CharField()

    internal_url = models.CharField(blank=True, null=True)

    scheduled_at = models.DateTimeField()
    sent_at = models.DateTimeField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = models.Manager()

    def build_notification(self) -> Notification:
        return Notification(
            user=self.user,
            content_title=self.content_title,
            content_body=self.content_body,
            content_icon=self.content_icon,
            internal_url=self.internal_url,
            partner_id="dinum-ami",
            send_status=self.user.last_logged_in is not None,
        )

    def publish(self):
        from ami.notification.push import push

        notification = self.build_notification()
        notification.save()
        self.sent_at = notification.created_at
        self.save()
        async_to_sync(push)(notification, True)

    @classmethod
    async def acreate_welcome_scheduled_notification(cls, user: User):
        scheduled_notification, _ = await cls.objects.aget_or_create(
            reference="ami:welcome",
            user=user,
            defaults={
                "content_title": "Bienvenue sur AMI 👋",
                "content_body": "Ici, vous pourrez gérer votre vie administrative, suivre l'avancement de vos démarches et recevoir des rappels personnalisés.",
                "content_icon": "fr-icon-information-line",
                "scheduled_at": timezone.now(),
            },
        )
        return scheduled_notification

    class Meta:
        db_table = "scheduled_notification"
        unique_together = (("user", "reference"),)
