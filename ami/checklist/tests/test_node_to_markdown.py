import xml.etree.ElementTree as ET

from ami.checklist.utils import node_to_markdown


def test_node_to_markdown():
    assert node_to_markdown(ET.fromstring("<Paragraphe>test</Paragraphe>")) == "test"
    assert (
        node_to_markdown(
            ET.fromstring("<Paragraphe>test <MiseEnEvidence>bold</MiseEnEvidence></Paragraphe>")
        )
        == "test **bold**"
    )
    assert (
        node_to_markdown(ET.fromstring("<Paragraphe>1<Exposant>er</Exposant> test</Paragraphe>"))
        == "1<sup>er</sup> test"
    )
    assert (
        node_to_markdown(
            ET.fromstring("<Paragraphe><Expression>expression</Expression></Paragraphe>")
        )
        == "*expression*"
    )
    assert (
        node_to_markdown(ET.fromstring("<Paragraphe>CO<Indice>2</Indice></Paragraphe>"))
        == "CO<sub>2</sub>"
    )


def test_node_to_markdown_space_before_parenthesis():
    assert (
        node_to_markdown(
            ET.fromstring("<Paragraphe><MiseEnEvidence>test </MiseEnEvidence>(or not)</Paragraphe>")
        )
        == "**test** (or not)"
    )


def test_node_to_markdown_stripped():
    assert (
        node_to_markdown(
            ET.fromstring("<Paragraphe>test <MiseEnEvidence>bold</MiseEnEvidence></Paragraphe>"),
            mode="stripped",
        )
        == "test bold"
    )
    assert (
        node_to_markdown(
            ET.fromstring("<Paragraphe>1<Exposant>er</Exposant> test</Paragraphe>"), mode="stripped"
        )
        == "1er test"
    )
