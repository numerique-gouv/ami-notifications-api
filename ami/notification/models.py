import uuid

from django.db import models
from django.utils import timezone

from ami.user.models import User


class Notification(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    content_body = models.CharField()
    sender = models.CharField()
    content_title = models.CharField()
    sa_orm_sentinel = models.IntegerField(blank=True, null=True)
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

    def build_notification(self) -> Notification:
        return Notification(
            user=self.user,
            content_title=self.content_title,
            content_body=self.content_body,
            content_icon=self.content_icon,
            sender=self.sender,
            send_status=self.user.last_logged_in is not None,
        )

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
