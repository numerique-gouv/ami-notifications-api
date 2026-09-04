import json
from io import StringIO

from django.core.management import call_command


def test_management_command(tmpdir):
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


def test_management_command_file_output(tmpdir):
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
