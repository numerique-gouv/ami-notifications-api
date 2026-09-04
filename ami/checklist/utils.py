import hashlib
import json
import re
import xml.etree.ElementTree as ET

from django.utils.text import slugify

MARKDOWN_MARKERS = {
    "full": {
        "MiseEnEvidence": ("**", "**"),
        "Expression": ("*", "*"),
        "Exposant": ("<sup>", "</sup>"),
        "Indice": ("<sub>", "</sub>"),
    },
    "stripped": {},
}


def node_to_markdown_parts(node, mode):
    if node.text:
        yield node.text
    for child in node:
        markers = MARKDOWN_MARKERS[mode].get(child.tag)
        if markers:
            yield markers[0]
            yield from node_to_markdown(child, mode=mode).strip()
            yield markers[1]
            if child.tail and child.tail.startswith("("):
                # force space to get correct markdown
                yield " "
        else:
            yield from node_to_markdown(child, mode=mode).strip()
        if child.tail:
            yield child.tail


def node_to_markdown(node, mode="full"):
    return "".join(node_to_markdown_parts(node, mode=mode))


def node_to_conditions(node):
    conditions = []
    for item in node:
        if item.tag == "ou":
            conditions.append({"type": "ou", "conditions": node_to_conditions(item)})
        else:
            conditions.append({"type": item.tag, "var": item.attrib["var"]})
    return conditions


def get_url_from_link_node(link_node):
    doc_id = link_node.attrib["LienPublication"]
    audience = link_node.attrib["audience"].lower()
    return f"https://www.service-public.gouv.fr/{audience}/vosdroits/{doc_id}"


class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, CheckList):
            return {"title": o.title, "items": o.items}
        return super().default(o)


class CheckList:
    title = None

    def __init__(self):
        self.items = []

    def add_item(self, node, section=None, condition=None):
        for item in node.findall("Item"):
            condition_elements = item.findall("Condition")
            conditions = []
            if condition_elements:
                assert len(condition_elements) == 1
                condition = condition_elements[0]
            assert len([x for x in item if x.tag == "Paragraphe"]) == 1
            paragraph = item.findall("Paragraphe")[0]
            text = node_to_markdown(paragraph).strip()
            id = None
            if condition is not None:
                conditions = node_to_conditions(condition)
            if id is None:
                id = hashlib.md5(ET.tostring(item)).hexdigest()[:12]
            links = []
            for link_node in paragraph.findall(".//*"):
                if not link_node.text:
                    continue
                if link_node.tag == "LienInterne":
                    links.append(
                        {
                            "url": get_url_from_link_node(link_node),
                            "text": link_node.attrib["commentaireLien"],
                            "type": link_node.attrib["type"],
                        }
                    )
                elif link_node.tag == "LienExterne":
                    links.append(
                        {
                            "url": link_node.attrib["URL"],
                            "text": node_to_markdown(link_node),
                            "external": True,
                        }
                    )
            self.add_item_real(text, id=id, section=section, conditions=conditions, links=links)

    def add_item_real(self, text, id, section=None, conditions=None, links=None):
        item = {"text": text, "id": id}
        if section:
            item["section"] = section
        if conditions:
            item["conditions"] = conditions
        if links:
            item["links"] = links
        self.items.append(item)


class Document:
    def __init__(self, root):
        self.current_section_id = None
        self.checklist = CheckList()
        self.title = None
        self.description = None

        try:
            self.title = root.find("{http://purl.org/dc/elements/1.1/}title").text
        except AttributeError:
            self.title = ""
        try:
            self.description = root.find("{http://purl.org/dc/elements/1.1/}description").text
        except AttributeError:
            self.description = ""

        self.sections = []
        self.build_checklist(parents=[root])

    def get_clean_title(self, title_element):
        title = node_to_markdown(title_element, mode="stripped").strip()
        title = re.sub(r"^\d+-\s+", "", title)
        return title

    def start_section(self, parents, child):
        section_title = None
        title_element = None

        try:
            situation_element = [x for x in parents if x.tag == "Situation"][-1]
            title_element = situation_element.find("Titre")
            if title_element is not None:
                section_title = self.get_clean_title(title_element)

            chapitre_element = [x for x in parents if x.tag == "Chapitre"][-1]
            if chapitre_element is not None:
                chapitre_title_element = chapitre_element.find("Titre")
                if chapitre_title_element is not None:
                    chapitre_title = self.get_clean_title(chapitre_title_element)
                    section_title = f"{section_title} - {chapitre_title}"

        except IndexError:
            pass

        if not section_title:
            # look for title in previous element
            parent = parents[-1]
            title_element = list(parent)[list(parent).index(child) - 1]
            section_title = self.get_clean_title(title_element)

        assert section_title
        section_id = slugify(section_title)
        self.sections.append({"title": section_title, "id": section_id})
        self.current_section_id = section_id

    def end_section(self):
        self.current_section_id = None

    def build_checklist(self, parents, condition=None):
        parent = parents[-1]
        for child in parent:
            if child.tag == "Liste" and child.attrib.get("type") == "caseACocher":
                if not self.current_section_id:
                    self.start_section(parents, child)
                self.checklist.add_item(child, section=self.current_section_id, condition=condition)
                continue
            elif child.tag == "FragmentConditionne" and child.findall("Liste"):
                self.build_checklist(parents + [child], condition=child.find("Condition"))
            elif child.tag == "Condition":
                continue
            else:
                if self.current_section_id:
                    self.end_section()
                self.build_checklist(parents + [child])

    def json(self):
        return json.dumps(
            {
                "title": self.title,
                "description": self.description,
                "sections": self.sections,
                "items": self.checklist.items,
            },
            cls=JSONEncoder,
            indent=2,
            ensure_ascii=False,
        )
