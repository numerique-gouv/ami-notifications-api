import uuid

from django.db import models

from ami.catalog.schemas import CatalogItem


class Procedure(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    partner_id = models.CharField()
    external_item_type = models.CharField()

    title = models.CharField()
    short_description = models.TextField()
    description = models.TextField()
    external_url = models.TextField()

    with_silent_login = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [("partner_id", "external_item_type")]

    def to_catalog_item(self):
        return CatalogItem(
            partner_id=self.partner_id,
            external_item_type=self.external_item_type,
            title=self.title,
            short_description=self.short_description,
            description=self.description,
            external_url=self.external_url,
            with_silent_login=self.with_silent_login,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )
