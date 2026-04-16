from django.core.management.base import BaseCommand

from ami.replication.models import AnonymizedUser
from ami.user.models import User


class Command(BaseCommand):
    help = "Replicate anonymised data to a new database"

    def handle(self, *args, **kwargs):
        page_size = 1000
        offset = 0

        while True:
            users = User.objects.all()[offset : offset + page_size]
            if not users:
                break
            for user in users:
                AnonymizedUser.from_user(user, using="data_ware_house")
            offset += page_size
