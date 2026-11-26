from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Init annuaire & sp actus"

    def handle(self, verbosity=1, **options):
        call_command("import_sp_actus", f"-v{verbosity}")
        call_command("init_annuaire", f"-v{verbosity}")
