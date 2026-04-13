import datetime

from django.core.management.base import BaseCommand
from django.utils.timezone import now

from ami.notification.models import ScheduledNotification


class Command(BaseCommand):
    help = "Delete already sent scheduled notifications"

    def handle(self, *args, **kwargs):
        scheduled_notifications = ScheduledNotification.objects.filter(
            sent_at__lt=now() - datetime.timedelta(days=6 * 30)
        )
        print(
            f"Deleting {scheduled_notifications.count()} scheduled notifications",
            scheduled_notifications,
        )
        scheduled_notifications.delete()
