import uuid

from django.db import models


class User(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    sa_orm_sentinel = models.IntegerField(blank=True, null=True)
    fc_hash = models.CharField(unique=True)
    last_logged_in = models.DateTimeField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "ami_user"


class Registration(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    subscription = models.JSONField(blank=True, null=True)
    sa_orm_sentinel = models.IntegerField(blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.PROTECT)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "registration"
