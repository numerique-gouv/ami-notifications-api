import os

import firebase_admin
from django.apps import AppConfig
from django.conf import settings


class NotificationConfig(AppConfig):
    name = "ami.notification"

    def ready(self) -> None:
        if os.getenv("GOOGLE_APPLICATION_CREDENTIALS") is None:
            # It's already set in Scalingo, locally it comes from .env.local, loaded in settings
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = settings.GOOGLE_APPLICATION_CREDENTIALS
        # This needs the "GOOGLE_APPLICATION_CREDENTIALS" env variable to be set to the secret json filename.
        # See the CONTRIBUTING.md file.
        firebase_admin.initialize_app()
