import uuid

from django.db import models

from ami.partner.models import partners
from ami.service.schemas import ServicesItem


class Service(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    partner_id = models.CharField(choices=[(p.id, p.name) for p in partners.values()])
    item_type = models.CharField()

    title = models.CharField()
    short_description = models.CharField("Service")
    description = models.TextField()
    url = models.CharField()

    with_silent_login = models.BooleanField(default=False)

    restricted_to = models.CharField(
        null=True,
        blank=True,
        help_text="fc_hash des utilisateurs autorisés à voir cette démarche dans le catalogue de démarches, séparés par un espace. "
        "Laisser vide pour un accès à tous les utilisateurs.",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [("partner_id", "item_type")]

    def to_services_item(self):
        return ServicesItem(
            partner_id=self.partner_id,
            item_type=self.item_type,
            title=self.title,
            short_description=self.short_description,
            description=self.description,
            url=self.url,
            with_silent_login=self.with_silent_login,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )
