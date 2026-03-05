from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from ami.notification.models import ScheduledNotification
from ami.notification.push import push


class Command(BaseCommand):
    help = "Create scheduled notifications to be distributed automatically"

    def handle(self, *args, **kwargs):
        now = timezone.now()
        scheduled_notifications = (
            ScheduledNotification.objects.select_for_update(skip_locked=True)
            .filter(
                scheduled_at__lt=now,
                sent_at__isnull=True,
            )
            .order_by("created_at")
        )
        with transaction.atomic():
            for notification in scheduled_notifications:
                self._publish_scheduled_notifications(notification)
        print(
            f"Pushed {scheduled_notifications.count()} scheduled notifications",
            scheduled_notifications,
        )

    def _publish_scheduled_notifications(self, scheduled_notification: ScheduledNotification):
        notification = scheduled_notification.build_notification()
        notification.save()
        scheduled_notification.sent_at = notification.created_at
        scheduled_notification.save()
        push(notification, True)
