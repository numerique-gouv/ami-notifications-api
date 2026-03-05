from django.core.management.base import BaseCommand

from ami.utils import generate_identity_tokens_in_file


class Command(BaseCommand):
    help = "Generate id tokens from a file."

    def add_arguments(self, parser):
        parser.add_argument("input_file_path", type=str)
        parser.add_argument("output_file_path", type=str)

    def handle(self, *args, **options):
        generate_identity_tokens_in_file(options["input_file_path"], options["output_file_path"])
