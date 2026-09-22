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
            if CheckList.objects.filter(external_id=external_id).exists():
                print(f"Check list {external_id} already exists")
                continue
            with open(os.path.join(dir_path, "data", f"{external_id}.json")) as fd:
                definition = json.loads(fd.read())
                CheckList.objects.create(
                    partner=partner,
                    external_id=external_id,
                    title=definition["title"],
                    definition=definition,
                )
                print(f"Check list {external_id} created")
