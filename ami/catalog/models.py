import uuid

from django.db import models


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
