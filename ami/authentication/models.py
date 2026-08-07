import uuid

from django.db import models

from ami.user.models import User


class Nonce(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    nonce = models.CharField(max_length=256)
    context = models.JSONField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "nonce"


class RevokedAuthToken(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    jti = models.CharField(unique=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "revoked_auth_token"


class UserPasskey(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.ForeignKey(User, on_delete=models.deletion.CASCADE)

    credential_id = models.CharField()
    credential_public_key = models.CharField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
