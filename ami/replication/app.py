import logging

from django.db import utils

from ami.replication.models import AnonymizedUser
from ami.user.models import User

logger = logging.getLogger(__name__)


def replicate_anonymized_users(chunk_size=1000):
    count = 0
    for user in User.objects.order_by("created_at").iterator(chunk_size=chunk_size):
        try:
            AnonymizedUser.from_user(user, using="data_ware_house")
        except utils.DatabaseError:
            logger.error("Replication error: Cannot access the datawarehouse")
        count += chunk_size
    logger.info(f"Replicated {count} users")
    return count
