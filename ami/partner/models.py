import uuid

from django.conf import settings
from django.db import models


class Partner(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    slug = models.SlugField(unique=True)
    name = models.CharField()
    icon = models.CharField(blank=True)
    consent_is_enabled = models.BooleanField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    @property
    def secret(self):
        return settings.PARTNERS_SECRETS[self.slug.replace("_", "-")]
