import xml.etree.ElementTree as ET

from django.core.management.base import BaseCommand

from ami.checklist.utils import Document


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("filename")
        parser.add_argument("-o", "--output", metavar="FILENAME")

    def handle(self, filename, **kwargs):
        doc = Document(ET.parse(filename).getroot())
        output_file = kwargs.get("output")
        if output_file:
            with open(output_file, "w") as fd:
                fd.write(doc.json() + "\n")
        else:
            self.stdout.write(doc.json() + "\n")
