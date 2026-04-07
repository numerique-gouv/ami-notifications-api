import datetime
import uuid

from django.conf import settings
from django.db import models
from django.utils.timezone import now


class FISession(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user_data = models.JSONField()
    state = models.CharField(max_length=256)
    nonce = models.CharField(max_length=256)
    code = models.CharField(max_length=256)
    access_token = models.CharField(max_length=256)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def is_expired(self):
        return self.created_at < now() - datetime.timedelta(seconds=settings.FI_SESSION_AGE)
