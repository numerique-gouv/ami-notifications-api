from django.core.management.base import BaseCommand

from ami.notification.models import ScheduledNotification


class Command(BaseCommand):
    help = "Delete already sent scheduled notifications"

    def handle(self, *args, **kwargs):
        scheduled_notifications = ScheduledNotification.to_delete.all()
        print(
            f"Deleting {scheduled_notifications.count()} scheduled notifications",
            scheduled_notifications,
        )
        scheduled_notifications.delete()
