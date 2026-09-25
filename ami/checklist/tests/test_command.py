import json
from io import StringIO

import pytest
from django.core.management import call_command

from ami.checklist.models import CheckList
from ami.partner.models import Partner


def test_management_command_create_checklist_from_doc(tmpdir):
    with open(tmpdir / "test.xml", "w") as fd:
        fd.write("""\
<Publication xmlns:dc="http://purl.org/dc/elements/1.1/"
             xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
             ID="F3109">
  <dc:title>Je crée une association</dc:title>
  <dc:description>J'organise des activités...</dc:description>
  <ListeSituations affichage="onglet">
    <Situation>
      <Titre>Cas général</Titre>
      <Liste type="caseACocher">
        <Item>
          <Paragraphe>Choisir le nom</Paragraphe>
        </Item>
        <Item>
          <Paragraphe>Rédiger les statuts</Paragraphe>
        </Item>
      </Liste>
    </Situation>
  </ListeSituations>
</Publication>""")

    out = StringIO()
    call_command("create_checklist_from_doc", tmpdir / "test.xml", stdout=out)
    assert json.loads(out.getvalue())["title"] == "Je crée une association"


def test_management_command_create_checklist_from_doc_file_output(tmpdir):
    with open(tmpdir / "test.xml", "w") as fd:
        fd.write("""\
<Publication xmlns:dc="http://purl.org/dc/elements/1.1/"
             xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
             ID="F3109">
  <dc:title>Je crée une association</dc:title>
  <dc:description>J'organise des activités...</dc:description>
  <ListeSituations affichage="onglet">
    <Situation>
      <Titre>Cas général</Titre>
      <Liste type="caseACocher">
        <Item>
          <Paragraphe>Choisir le nom</Paragraphe>
        </Item>
        <Item>
          <Paragraphe>Rédiger les statuts</Paragraphe>
        </Item>
      </Liste>
    </Situation>
  </ListeSituations>
</Publication>""")

    call_command("create_checklist_from_doc", tmpdir / "test.xml", "--output", tmpdir / "test.json")
    with open(tmpdir / "test.json") as fd:
        assert json.load(fd)["title"] == "Je crée une association"


@pytest.mark.django_db
def test_management_command_init_checklists(partner_psl: Partner):
    assert CheckList.objects.count() == 0

    call_command("init_checklists")

    assert CheckList.objects.count() == 4
    assert CheckList.objects.filter(
        partner=partner_psl, external_id="CNMSS001", title="Je suis affecté à l'étranger"
    ).exists()
    assert CheckList.objects.filter(
        partner=partner_psl, external_id="F16225", title="Je deviens parent"
    ).exists()
    assert CheckList.objects.filter(
        partner=partner_psl, external_id="F3109", title="Je crée une association"
    ).exists()
    assert CheckList.objects.filter(
        partner=partner_psl,
        external_id="F39617",
        title="Je souhaite accompagner mon enfant de 15 à 18 ans dans ses droits et ses démarches",
    ).exists()

    call_command("init_checklists")

    assert CheckList.objects.count() == 4


@pytest.mark.django_db
def test_management_command_init_checklists_update(partner_psl: Partner, partner_dn: Partner):
    assert CheckList.objects.count() == 0

    call_command("init_checklists")
    checklist_f16225 = CheckList.objects.get(external_id="F16225")
    CheckList.objects.filter(external_id="CNMSS001").update(
        partner=partner_dn, definition={"foo": "bar"}
    )

    # update
    call_command("init_checklists")
    checklist = CheckList.objects.get(external_id="CNMSS001")
    assert checklist.partner == partner_dn  # partner is left intact
    assert checklist.definition != {"foo": "bar"}  # definition is updated

    # check unchanged list was not updated
    assert checklist_f16225.updated_at == CheckList.objects.get(external_id="F16225").updated_at
