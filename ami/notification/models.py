import datetime
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

    content_body = models.CharField()
    sender = models.CharField()
    content_title = models.CharField()
    sa_orm_sentinel = models.IntegerField(blank=True, null=True)
    user_id: uuid.UUID  # For typing purposes: this is only a type annotation
    user = models.ForeignKey(User, models.PROTECT)
    content_icon = models.CharField(blank=True, null=True)
    item_type = models.CharField(blank=True, null=True)
    item_id = models.CharField(blank=True, null=True)
    item_status_label = models.CharField(blank=True, null=True)
    item_generic_status = models.CharField(blank=True, null=True)
    item_canal = models.CharField(blank=True, null=True)
    item_milestone_start_date = models.DateTimeField(blank=True, null=True)
    item_milestone_end_date = models.DateTimeField(blank=True, null=True)
    item_external_url = models.CharField(blank=True, null=True)
    send_date = models.DateTimeField(default=timezone.now)
    read = models.BooleanField(default=False)
    try_push = models.BooleanField(blank=True, null=True)
    send_status = models.BooleanField(blank=True, null=True)
    partner_id = models.CharField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "notification"


class ScheduledNotificationToPublishManager(models.Manager):
    def get_queryset(self):
        now = timezone.now()
        queryset = (
            super()
            .get_queryset()
            .filter(
                scheduled_at__lt=now,
                sent_at__isnull=True,
            )
            .order_by("created_at")
        )
        return queryset

    def publish(self):
        queryset = self.get_queryset()
        for scheduled_notification in queryset:
            scheduled_notification.publish()
        return queryset


class ScheduledNotificationToDeleteManager(models.Manager):
    def get_queryset(self):
        now = timezone.now()
        queryset = super().get_queryset().filter(sent_at__lt=now - datetime.timedelta(days=6 * 30))
        return queryset

    def delete(self):
        queryset = self.get_queryset()
        queryset.delete()
        return queryset


class ScheduledNotification(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.ForeignKey(User, models.PROTECT)
    content_title = models.CharField()
    content_body = models.CharField()
    content_icon = models.CharField()
    sender = models.CharField()
    reference = models.CharField()
    scheduled_at = models.DateTimeField()
    sent_at = models.DateTimeField(blank=True, null=True)
    sa_orm_sentinel = models.IntegerField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = models.Manager()
    to_publish = ScheduledNotificationToPublishManager()
    to_delete = ScheduledNotificationToDeleteManager()

    def build_notification(self) -> Notification:
        return Notification(
            user=self.user,
            content_title=self.content_title,
            content_body=self.content_body,
            content_icon=self.content_icon,
            sender=self.sender,
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
    def create_welcome_scheduled_notification(cls, user: User):
        scheduled_notification, _ = cls.objects.get_or_create(
            reference="ami:welcome",
            user=user,
            defaults={
                "content_title": "Bienvenue sur AMI 👋",
                "content_body": "Ici, vous pourrez gérer votre vie administrative, suivre l'avancement de vos démarches et recevoir des rappels personnalisés.",
                "content_icon": "fr-icon-information-line",
                "reference": "ami:welcome",
                "scheduled_at": timezone.now(),
                "sender": "AMI",
            },
        )
        return scheduled_notification

    class Meta:
        db_table = "scheduled_notification"
        unique_together = (("user", "reference"),)
