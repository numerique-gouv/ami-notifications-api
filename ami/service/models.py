import uuid

from django.db import models


class Service(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    partner_id = models.CharField()
    item_type = models.CharField()

    title = models.CharField()
    short_description = models.TextField()
    description = models.TextField()
    url = models.TextField()

    with_silent_login = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [("partner_id", "item_type")]
