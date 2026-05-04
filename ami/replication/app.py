import logging

from django.db import utils

from ami.notification.models import Notification
from ami.replication.models import AnonymizedNotification, AnonymizedRegistration, AnonymizedUser
from ami.user.models import Registration, User

logger = logging.getLogger(__name__)


def replicate_anonymized_users(chunk_size=1000):
    count = 0
    for user in User.objects.order_by("created_at").iterator(chunk_size=chunk_size):
        try:
            AnonymizedUser.from_user(user, using="data_ware_house")
        except utils.DatabaseError:
            logger.error("Replication users error: Cannot access the datawarehouse")
        count += chunk_size
    logger.info(f"Replicated {count} users")
    return count


def replicate_anonymized_notifications(chunk_size=1000):
    count = 0
    for notification in Notification.objects.order_by("created_at").iterator(chunk_size=chunk_size):
        try:
            AnonymizedNotification.from_notification(notification, using="data_ware_house")
        except utils.DatabaseError:
            logger.error("Replication error: Cannot access the datawarehouse")
        count += chunk_size
    logger.info(f"Replicated {count} notifications")
    return count


def replicate_anonymized_registrations(chunk_size=1000):
    count = 0
    for registration in Registration.objects.order_by("created_at").iterator(chunk_size=chunk_size):
        try:
            AnonymizedRegistration.from_registration(registration, using="data_ware_house")
        except utils.DatabaseError:
            logger.error("Replication error: Cannot access the datawarehouse")
        count += chunk_size
    logger.info(f"Replicated {count} registrations")
    return count
