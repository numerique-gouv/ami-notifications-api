import datetime

from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.utils.timezone import now

from ami.authentication.models import Nonce
from ami.fi.models import FISession
from ami.notification.models import ScheduledNotification


class Command(BaseCommand):
    help = "Cleanup obsolete database objects"

    def handle(self, verbosity=1, **options):
        call_command("clearsessions", f"-v{verbosity}")

        fi_sessions = FISession.objects.filter(
            created_at__lt=now() - datetime.timedelta(seconds=settings.FI_SESSION_AGE)
        )
        if verbosity:
            self.stdout.write(f"Deleting {fi_sessions.count()} FI sessions")
        fi_sessions.delete()

        scheduled_notifications = ScheduledNotification.objects.filter(
            sent_at__lt=now() - datetime.timedelta(days=6 * 30)
        )
        if verbosity:
            self.stdout.write(f"Deleting {scheduled_notifications.count()} scheduled notifications")
        scheduled_notifications.delete()

        nonces = Nonce.objects.filter(created_at__lt=now() - datetime.timedelta(hours=1))
        if verbosity:
            self.stdout.write(f"Deleting {nonces.count()} nonces")
        nonces.delete()
