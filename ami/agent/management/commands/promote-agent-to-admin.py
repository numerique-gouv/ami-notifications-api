from django.core.management.base import BaseCommand, CommandError

from ami.agent.models import Agent


class Command(BaseCommand):
    help = "Promote agent to admin"

    def add_arguments(self, parser):
        parser.add_argument("email", type=str)

    def handle(self, *args, **options):
        email = options["email"]
        try:
            agent = Agent.objects.get(user__email=email)
        except Agent.DoesNotExist:
            raise CommandError('Agent with email "%s" does not exist' % email)

        agent.role = Agent.Role.ADMIN
        agent.save()

        self.stdout.write(self.style.SUCCESS('Successfully promoted agent "%s" to admin' % agent))
