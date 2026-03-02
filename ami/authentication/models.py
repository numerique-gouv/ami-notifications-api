import uuid

from django.db import models


class Nonce(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    nonce = models.CharField(max_length=256)
    sa_orm_sentinel = models.IntegerField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "nonce"


class RevokedAuthToken(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    jti = models.CharField(unique=True)
    sa_orm_sentinel = models.IntegerField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "revoked_auth_token"
