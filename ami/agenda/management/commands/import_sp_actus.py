import datetime
import logging
import re
import xml.etree.ElementTree as ET

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from ami.agenda.models import SpActuItem
from ami.checklist.utils import node_to_markdown
from ami.utils.httpx import httpxClient

logger = logging.getLogger(__name__)


class EcheanceParseException(Exception):
    pass


MONTH_ABBR = {
    "janv.": 1,
    "févr.": 2,
    "mars": 3,
    "avr.": 4,
    "mai": 5,
    "juin": 6,
    "juil.": 7,
    "août": 8,
    "sept.": 9,
    "oct.": 10,
    "nov.": 11,
    "déc.": 12,
}


def get_text(node, child):
    child_node = node.find(child)
    return child_node.text if child_node is not None else None


def get_date_from_tuple(date_tuple):
    if date_tuple is None:
        return None
    return datetime.date(
        int(date_tuple[2]), MONTH_ABBR[date_tuple[1]], int(date_tuple[0])
    ).strftime("%Y-%m-%d")


def parse_echeance(string):
    dates = [list(x) for x in re.findall(r"(\d+)\s([\w]{3,4}\.?)\s(\d{4})?", string)]
    if not dates:
        raise EcheanceParseException()
    start_date, end_date, unique_date = None, None, None
    if len(dates) == 2:
        if not dates[0][2]:  # no year, as in Du 21 nov. au 27 nov. 2026
            dates[0][2] = dates[1][2]
        start_date, end_date = get_date_from_tuple(dates[0]), get_date_from_tuple(dates[1])
    elif string.startswith("À partir"):
        start_date = get_date_from_tuple(dates[0])
    elif string.startswith(("Jusqu'au", "Avant le")):
        end_date = get_date_from_tuple(dates[0])
    else:
        unique_date = get_date_from_tuple(dates[0])
    return start_date, end_date, unique_date


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("-s", "--simulate", action="store_true")

    def handle(self, **kwargs):
        self.theme_codes = {}

        with httpxClient() as httpx_client:
            response = httpx_client.get(settings.COMARQUAGE_ACTUS_URL)
        if response.status_code != 200:
            raise CommandError(f"failed: response status code: {response.status_code}")

        root = ET.fromstring(response.text)
        for actu in root.findall("RefActualite"):
            echeance_node = actu.find("Echeance")
            if echeance_node is None:
                continue
            try:
                start_date, end_date, unique_date = parse_echeance(echeance_node.text)
            except EcheanceParseException:
                logger.error(
                    "failed to parse <Echeance> of %s (%s)"
                    % (actu.attrib["LienPublication"], echeance_node.text)
                )
                continue

            external_id = actu.attrib["LienPublication"]

            introduction = "\n\n".join([node_to_markdown(x) for x in actu.findall(".//Paragraphe")])
            themes = [self.get_theme_label(x) for x in actu.attrib.get("themes", "").split(",")]
            themes = [x for x in themes if x]

            actu_data = {
                "title": get_text(actu, "Titre"),
                "initial_publication_date": actu.attrib["datePremiereMiseEnLigne"],
                "last_update_date": actu.attrib.get("dateMaj"),
                "themes": themes,
                "date": unique_date,
                "start_date": start_date,
                "end_date": end_date,
                "url": f"{settings.SP_ACTU_BASE_URL}{actu.attrib['LienPublication']}",
            }

            if kwargs["verbosity"] > 1:
                self.stdout.write(f"# {actu_data['title']}\n")
                if actu_data["date"]:
                    self.stdout.write(f"- date : {actu_data['unique_date']}\n")
                else:
                    self.stdout.write(
                        f"- dates : {actu_data['start_date'] or ''} → {actu_data['end_date'] or ''}"
                    )
                if themes:
                    self.stdout.write(f"- thèmes : {' · '.join(themes)}\n")
                self.stdout.write(f"- publication: {actu_data['initial_publication_date']}\n")
                if actu_data["last_update_date"]:
                    self.stdout.write(f"- mise à jour : {actu_data['last_update_date']}\n")
                self.stdout.write(f"\n{introduction}\n\n→ {actu_data['url']}\n\n\n")

            if kwargs.get("simulate"):
                continue

            actu, created = SpActuItem.objects.get_or_create(
                external_id=external_id, defaults=actu_data
            )
            if not created:
                changed = False
                for attr, value in actu_data.items():
                    if getattr(actu, attr, None) != value:
                        setattr(actu, attr, value)
                        changed = True
                if changed:
                    actu.save()

        if kwargs["verbosity"] > 1:
            self.stdout.write("## Themes\n")
            self.stdout.write("\n".join(f"- {k}: {v}" for k, v in self.theme_codes.items()))

    def get_theme_label(self, code):
        if not code or not code.startswith("N"):
            return None
        if code in self.theme_codes:
            return self.theme_codes[code]
        with httpxClient() as httpx_client:
            response = httpx_client.get(f"{settings.COMARQUAGE_THEMES_BASE_URL}{code}.xml")
        if response.status_code != 200:
            logger.error("failed to get theme (%s)" % (code))
            return None
        root = ET.fromstring(response.text)
        title = get_text(root, "{http://purl.org/dc/elements/1.1/}title")
        self.theme_codes[code] = title
        return title
