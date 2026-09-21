import uuid

from django.db import models

from ami.partner.models import Partner


class CheckList(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    partner = models.ForeignKey(Partner, models.PROTECT, db_column="partner_uuid")

    external_id = models.CharField(unique=True)
    title = models.CharField()
    icon = models.CharField(blank=True)
    definition = models.JSONField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
