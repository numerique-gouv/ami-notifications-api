import uuid

from django.contrib.postgres.fields import ArrayField
from django.db import models


class SpActuItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    external_id = models.CharField(unique=True)

    title = models.CharField()
    date = models.DateField(null=True)
    start_date = models.DateField(null=True)
    end_date = models.DateField(null=True)
    themes = ArrayField(models.CharField(max_length=100, blank=True), null=True)
    url = models.CharField()
    initial_publication_date = models.DateField()
    last_update_date = models.DateField(null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
