import uuid

from django.db import models


class Mairie(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    code_insee_commune = models.CharField(unique=True)
    id_service_local = models.CharField()
    nom = models.CharField()
    url_service_public = models.CharField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
