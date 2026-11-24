import datetime

import pytest
from django.conf import settings
from django.core.management import call_command

from ami.agenda.management.commands.import_sp_actus import EcheanceParseException, parse_echeance
from ami.agenda.models import SpActuItem
from ami.utils.httpx import URL

EXAMPLE_RESPONSE = """<?xml version="1.0" encoding="UTF-8"?>
<IndexActualite xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="../Schemas/3.5/indexes/IndexActualite.xsd">
  <dc:date>2026-11-20T02:38:29</dc:date>
  <RefActualite LienPublication="A19140" type="bref" audience="Particuliers" aLaUne="oui" focus="non" themes="N19811" sujets="social" datePremiereMiseEnLigne="2026-11-19">
    <Date>Publié le 19 novembre 2026</Date>
    <SurTitre>Actes médicaux</SurTitre>
    <Titre>Un décret vient encadrer la pratique de la médecine esthétique</Titre>
    <Introduction>
      <Texte>
        <Paragraphe>De nouvelles mesures sont mises en place pour encadrer davantage la pratique médicale des actes à visée esthétique. Régulation de l'activité, formation des médecins et information des patients... Un décret paru au <Expression>Journal officiel</Expression> du 14%novembre%2026 impose de nouvelles règles aux professionnels concernés.</Paragraphe>
      </Texte>
    </Introduction>
  </RefActualite>
  <RefActualite LienPublication="A18451" type="bref" audience="Particuliers" aLaUne="oui" focus="non" themes="N19803,N19805" sujets="conso" datePremiereMiseEnLigne="2025-09-17" dateMaj="2026-11-17">
    <Date>Publié le 17 novembre 2026</Date>
    <Echeance misEnAvant="non">À partir du 20 nov. 2026</Echeance>
    <SurTitre>Emprunts</SurTitre>
    <Titre>Crédits à la consommation : les règles évoluent pour prévenir le surendettement</Titre>
    <Introduction>
      <Texte>
        <Paragraphe>De nouvelles mesures viennent encadrer les contrats de crédit à la consommation (crédits gratuits, paiements fractionnés, mini-crédits...) à compter du 20%novembre. L’objectif est de mieux protéger les consommateurs et de prévenir le surendettement. <Expression>Service Public</Expression> vous explique.</Paragraphe>
      </Texte>
    </Introduction>
  </RefActualite>
</IndexActualite>"""

N19803_RESPONSE = """<?xml version="1.0" encoding="UTF-8"?>
<Publication xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" ID="N19803" type="Theme" xsi:noNamespaceSchemaLocation="../Schemas/3.5/Publication.xsd" spUrl="https://www.service-public.gouv.fr/particuliers/vosdroits/N19803">
  <dc:title>Argent - Impôts - Consommation</dc:title>
</Publication>"""

N19805_RESPONSE = """<?xml version="1.0" encoding="UTF-8"?>
<Publication xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" ID="N19805" type="Theme" xsi:noNamespaceSchemaLocation="../Schemas/3.5/Publication.xsd" spUrl="https://www.service-public.gouv.fr/particuliers/vosdroits/N19805">
  <dc:title>Famille - Scolarité</dc:title>
</Publication>"""


def test_management_command_import_sp_actus(db, httpx_mock):
    httpx_mock.add_response(
        url=URL(settings.COMARQUAGE_ACTUS_URL), text=EXAMPLE_RESPONSE, is_reusable=True
    )
    httpx_mock.add_response(
        url=URL(f"{settings.COMARQUAGE_THEMES_BASE_URL}N19803.xml"),
        text=N19803_RESPONSE,
        is_reusable=True,
    )
    httpx_mock.add_response(
        url=URL(f"{settings.COMARQUAGE_THEMES_BASE_URL}N19805.xml"),
        text=N19805_RESPONSE,
        is_reusable=True,
    )

    call_command("import_sp_actus", "--simulate", "--verbosity", "2")
    assert SpActuItem.objects.all().count() == 0

    call_command("import_sp_actus")
    assert SpActuItem.objects.all().count() == 1

    call_command("import_sp_actus")
    assert SpActuItem.objects.all().count() == 1

    sp_actu = SpActuItem.objects.all().first()
    assert sp_actu
    assert set(sp_actu.themes) == {"Argent - Impôts - Consommation", "Famille - Scolarité"}
    assert (
        sp_actu.title
        == "Crédits à la consommation : les règles évoluent pour prévenir le surendettement"
    )
    assert sp_actu.last_update_date == datetime.date(2026, 11, 17)
    assert sp_actu.initial_publication_date == datetime.date(2025, 9, 17)
    assert sp_actu.start_date == datetime.date(2026, 11, 20)
    assert sp_actu.url == "https://www.service-public.gouv.fr/particuliers/actualites/A18451"


def test_parse_echeance():
    assert parse_echeance("À partir du 17 nov. 2026") == ("2026-11-17", None, None)
    assert parse_echeance("Jusqu'au 31 déc. 2026") == (None, "2026-12-31", None)
    assert parse_echeance("Du 14 sept. 2026 au 28 févr. 2027") == ("2026-09-14", "2027-02-28", None)
    assert parse_echeance("Du 21 nov. au 27 nov. 2026") == ("2026-11-21", "2026-11-27", None)
    assert parse_echeance("Le 2 sept. 2027") == (None, None, "2027-09-02")


def test_parse_echeance_exception():
    with pytest.raises(EcheanceParseException):
        assert parse_echeance("Avant mars 2027")
