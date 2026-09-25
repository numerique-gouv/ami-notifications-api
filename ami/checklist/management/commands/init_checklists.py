import json
import os

from django.core.management.base import BaseCommand

from ami.checklist.models import CheckList
from ami.partner.models import Partner

dir_path = os.path.dirname(os.path.realpath(__file__))


class Command(BaseCommand):
    def handle(self, **kwargs):
        partner = Partner.objects.get(slug="psl")
        for external_id in ["CNMSS001", "F16225", "F3109", "F39617"]:
            with open(os.path.join(dir_path, "data", f"{external_id}.json")) as fd:
                definition = json.loads(fd.read())
                checklist, created = CheckList.objects.get_or_create(
                    external_id=external_id,
                    defaults={
                        "partner": partner,
                        "title": definition["title"],
                        "definition": definition,
                    },
                )
                if created:
                    self.stdout.write(f"Check list {external_id} created")
                elif checklist.definition != definition:
                    checklist.definition = definition
                    checklist.save()
                    self.stdout.write(f"Check list {external_id} updated")
                else:
                    self.stdout.write(f"Check list {external_id} already up-to-date")
