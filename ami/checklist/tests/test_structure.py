import xml.etree.ElementTree as ET

from ami.checklist.utils import CheckList, Document


def test_basic():
    doc = Document(
        ET.fromstring("""<?xml version="1.0" encoding="UTF-8"?>
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
    )
    assert doc.title == "Je crée une association"
    assert doc.description == "J'organise des activités..."
    assert len(doc.sections) == 1
    assert doc.sections[0]["title"] == "Cas général"
    assert len(doc.checklist.items) == 2
    assert doc.checklist.items[0]["text"] == "Choisir le nom"
    assert doc.checklist.items[0]["section"] == doc.sections[0]["id"]
    assert doc.checklist.items[1]["text"] == "Rédiger les statuts"


def test_checklist_with_title_in_previous_paragraph():
    doc = Document(
        ET.fromstring("""<?xml version="1.0" encoding="UTF-8"?>
<Publication xmlns:dc="http://purl.org/dc/elements/1.1/"
             xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
             ID="F16225">
  <Conclusion>
    <Paragraphe>
      <MiseEnEvidence>1- Pendant la grossesse</MiseEnEvidence>
    </Paragraphe>
    <Liste type="caseACocher">
      <Item>
        <Paragraphe>Choisir le nom</Paragraphe>
      </Item>
    </Liste>
    <Liste type="caseACocher">
      <Item>
        <Paragraphe>Mettre à jour votre carte vitale</Paragraphe>
      </Item>
    </Liste>
    <Paragraphe>
      <MiseEnEvidence>2- Après la naissance</MiseEnEvidence>
    </Paragraphe>
    <Liste type="caseACocher">
      <Item>
        <Paragraphe>Déclarer la naissance</Paragraphe>
      </Item>
    </Liste>
  </Conclusion>
</Publication>""")
    )
    assert len(doc.sections) == 2
    assert doc.sections[0]["title"] == "Pendant la grossesse"
    assert doc.sections[1]["title"] == "Après la naissance"
    assert doc.checklist.items[0]["text"] == "Choisir le nom"
    assert doc.checklist.items[-1]["text"] == "Déclarer la naissance"


def test_checklist_with_conditional_fragment():
    doc = Document(
        ET.fromstring("""<?xml version="1.0" encoding="UTF-8"?>
<Publication xmlns:dc="http://purl.org/dc/elements/1.1/"
             xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
             ID="F16225">
  <Conclusion>
    <Paragraphe>
      <MiseEnEvidence>1- Pendant la grossesse</MiseEnEvidence>
    </Paragraphe>
    <Liste type="caseACocher">
      <Item>
        <Paragraphe>Choisir le nom</Paragraphe>
      </Item>
    </Liste>
    <FragmentConditionne>
      <Condition>
        <estVrai var="T11332"/>
      </Condition>
      <Liste type="caseACocher">
        <Item>
          <Paragraphe>Mettre à jour votre carte vitale</Paragraphe>
        </Item>
      </Liste>
    </FragmentConditionne>
  </Conclusion>
</Publication>""")
    )
    assert len(doc.sections) == 1
    assert doc.checklist.items[-1]["text"] == "Mettre à jour votre carte vitale"
    assert doc.checklist.items[-1]["conditions"] == [{"type": "estVrai", "var": "T11332"}]


def test_checklist_with_situation_and_chapitre():
    doc = Document(
        ET.fromstring("""<?xml version="1.0" encoding="UTF-8"?>
<Publication xmlns:dc="http://purl.org/dc/elements/1.1/"
             xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
             ID="CNMSS001">
  <ListeSituations affichage="onglet">
    <Situation>
      <Titre>Avant mon départ</Titre>
      <Texte>
        <Chapitre>
          <Titre>Pour tous les militaires</Titre>
          <Liste type="caseACocher">
            <Item>
              <Paragraphe>Déclarer mon affectation</Paragraphe>
            </Item>
          </Liste>
         </Chapitre>
        <Chapitre>
          <Titre>Si le conjoint m'accompagne</Titre>
          <Liste type="caseACocher">
            <Item>
              <Paragraphe>Vérifier les droits de mon conjoint</Paragraphe>
            </Item>
          </Liste>
         </Chapitre>
       </Texte>
    </Situation>
    <Situation>
      <Titre>Pendant mon affectation</Titre>
      <Texte>
        <Chapitre>
          <Titre>Pour tous les militaires</Titre>
          <Liste type="caseACocher">
            <Item>
              <Paragraphe>Demander le remboursement de mes soins</Paragraphe>
            </Item>
          </Liste>
         </Chapitre>
        <Chapitre>
          <Titre>Pour les enfants</Titre>
          <Liste type="caseACocher">
            <Item>
              <Paragraphe>Bénéficier, si nécessaire, de la téléorthophonie</Paragraphe>
            </Item>
          </Liste>
         </Chapitre>
       </Texte>
    </Situation>
  </ListeSituations>
</Publication>""")
    )
    assert len(doc.sections) == 4
    assert [x["title"] for x in doc.sections] == [
        "Avant mon départ - Pour tous les militaires",
        "Avant mon départ - Si le conjoint m'accompagne",
        "Pendant mon affectation - Pour tous les militaires",
        "Pendant mon affectation - Pour les enfants",
    ]
    assert len(set(x["id"] for x in doc.sections)) == 4


def test_item_with_links():
    checklist = CheckList()
    checklist.add_item(
        ET.fromstring("""\
<Liste type="caseACocher">
  <Item>
    <Paragraphe>paragraph with
      <LienInterne LienPublication="F31494" type="Fiche Question-réponse conditionnée" audience="Particuliers"
        commentaireLien="Peut-on choisir librement le nom d'une association ?">internal link</LienInterne>
        and
      <LienExterne URL="https://associations.gouv.fr/guid-asso">external link</LienExterne>
    </Paragraphe>
  </Item>
</Liste>""")
    )
    assert checklist.items[0]["links"] == [
        {
            "text": "Peut-on choisir librement le nom d'une association ?",
            "type": "Fiche Question-réponse conditionnée",
            "url": "https://www.service-public.gouv.fr/particuliers/vosdroits/F31494",
        },
        {
            "external": True,
            "text": "external link",
            "url": "https://associations.gouv.fr/guid-asso",
        },
    ]


def test_item_with_condition():
    checklist = CheckList()
    checklist.add_item(
        ET.fromstring("""
<Liste type="caseACocher">
  <Item>
    <Condition>
      <ou>
        <estFaux var="absence_compte_cnmss"/>
        <estIndefini var="absence_compte_cnmss"/>
      </ou>
    </Condition>
    <Paragraphe>Créer mon compte CNMSS</Paragraphe>
  </Item>
</Liste>""")
    )
    assert checklist.items[0]["conditions"] == [
        {
            "type": "ou",
            "conditions": [
                {"type": "estFaux", "var": "absence_compte_cnmss"},
                {"type": "estIndefini", "var": "absence_compte_cnmss"},
            ],
        }
    ]
