from django.core.management.base import BaseCommand

from ami.notification.models import ScheduledNotification


class Command(BaseCommand):
    help = "Create scheduled notifications to be automatically send"

    def handle(self, *args, **kwargs):
        scheduled_notifications = ScheduledNotification.to_publish.publish()
        print(
            f"Pushed {scheduled_notifications.count()} scheduled notifications",
            scheduled_notifications,
        )
