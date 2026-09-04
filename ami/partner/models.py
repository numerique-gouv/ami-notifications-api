import uuid

from django.conf import settings
from django.db import models

from ami.partner.schemas import PartnersItem


class Partner(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    slug = models.SlugField(unique=True)
    name = models.CharField()
    icon = models.CharField(blank=True)
    link = models.CharField(blank=True, null=True)
    consent_is_enabled = models.BooleanField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    @property
    def secret(self):
        return settings.PARTNERS_SECRETS.get(self.slug.replace("_", "-")) or ""

    def to_partners_item(self):
        return PartnersItem(
            slug=self.slug,
            name=self.name,
            link=self.link,
            consent_is_enabled=self.consent_is_enabled,
        )
