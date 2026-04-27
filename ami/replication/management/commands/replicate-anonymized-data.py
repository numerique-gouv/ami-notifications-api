import logging

from django.core.management.base import BaseCommand

from ami.replication.app import replicate_anonymized_users

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Replicate anonymised data to a new database (Data Ware House)"

    def handle(self, *args, **kwargs):
        logger.info("Starting anonymized data replication")
        count = replicate_anonymized_users()
        logger.info(f"Anonymized data replication complete. Total users replicated: {count}")
