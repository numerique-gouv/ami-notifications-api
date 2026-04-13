import datetime

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils.timezone import now

from ami.fi.models import FISession


class Command(BaseCommand):
    help = "Delete expired FI Sessions"

    def handle(self, *args, **kwargs):
        fi_sessions = FISession.objects.filter(
            created_at__lt=now() - datetime.timedelta(seconds=settings.FI_SESSION_AGE)
        )
        print(f"Deleting {fi_sessions.count()} FI Sessions")
        fi_sessions.delete()
