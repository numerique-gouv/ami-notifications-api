import logging

from django.core.management.base import BaseCommand

from ami.replication.app import replicate_anonymized_data

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Replicate anonymised data to a new database (Data Ware House)"

    def handle(self, *args, **kwargs):
        logger.info("Starting anonymized data replication ... ")
        replicate_anonymized_data()
        logger.info("Anonymized data replication complete !")
