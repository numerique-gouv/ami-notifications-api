import logging

from django.core.management.base import BaseCommand
from django.db import utils

from ami.replication.models import AnonymizedUser
from ami.user.models import User

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Replicate anonymised data to a new database"

    def handle(self, *args, **kwargs):
        page_size = 1000
        offset = 0
        total = 0

        logger.info("Starting anonymized data replication")

        while True:
            users = User.objects.all()[offset : offset + page_size]
            if not users:
                break
            for user in users:
                try:
                    AnonymizedUser.from_user(user, using="data_ware_house")
                except utils.DatabaseError:
                    logger.error("Replication error: Cannot access the datawarehouse")
            count = len(users)
            total += count
            offset += page_size
            logger.info(f"Replicated {count} users (total: {total})")

        logger.info(f"Anonymized data replication complete. Total users replicated: {total}")
