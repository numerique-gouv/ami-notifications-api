from django.core.management.base import BaseCommand
from django.utils.timezone import now

from ami.notification.models import ScheduledNotification


class Command(BaseCommand):
    help = "Create scheduled notifications to be distributed automatically"

    def handle(self, *args, **kwargs):
        scheduled_notifications = ScheduledNotification.objects.filter(
            scheduled_at__lt=now(),
            sent_at__isnull=True,
        ).order_by("created_at")
        scheduled_notifications_count = 0
        for scheduled_notification in scheduled_notifications:
            scheduled_notification.publish()
            scheduled_notifications_count += 1
        print(
            f"Pushed {scheduled_notifications_count} scheduled notifications",
            scheduled_notifications,
        )
