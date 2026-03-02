from django.db import models


class AlembicVersion(models.Model):
    version_num = models.CharField(primary_key=True, max_length=32)

    class Meta:
        db_table = "alembic_version"


class AmiUser(models.Model):
    sa_orm_sentinel = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    id = models.UUIDField(primary_key=True)
    fc_hash = models.CharField(unique=True)
    last_logged_in = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = "ami_user"


class Nonce(models.Model):
    nonce = models.CharField(max_length=256)
    id = models.UUIDField(primary_key=True)
    sa_orm_sentinel = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        db_table = "nonce"


class Notification(models.Model):
    created_at = models.DateTimeField()
    content_body = models.CharField()
    sender = models.CharField()
    content_title = models.CharField()
    sa_orm_sentinel = models.IntegerField(blank=True, null=True)
    updated_at = models.DateTimeField()
    id = models.UUIDField(primary_key=True)
    user = models.ForeignKey(AmiUser, models.DO_NOTHING)
    content_icon = models.CharField(blank=True, null=True)
    item_type = models.CharField(blank=True, null=True)
    item_id = models.CharField(blank=True, null=True)
    item_status_label = models.CharField(blank=True, null=True)
    item_generic_status = models.CharField(blank=True, null=True)
    item_canal = models.CharField(blank=True, null=True)
    item_milestone_start_date = models.DateTimeField(blank=True, null=True)
    item_milestone_end_date = models.DateTimeField(blank=True, null=True)
    item_external_url = models.CharField(blank=True, null=True)
    send_date = models.DateTimeField()
    read = models.BooleanField()
    try_push = models.BooleanField(blank=True, null=True)
    send_status = models.BooleanField(blank=True, null=True)
    partner_id = models.CharField(blank=True, null=True)

    class Meta:
        db_table = "notification"


class Registration(models.Model):
    subscription = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField()
    sa_orm_sentinel = models.IntegerField(blank=True, null=True)
    updated_at = models.DateTimeField()
    id = models.UUIDField(primary_key=True)
    user = models.ForeignKey(AmiUser, models.DO_NOTHING)

    class Meta:
        db_table = "registration"


class RevokedAuthToken(models.Model):
    jti = models.CharField(unique=True)
    id = models.UUIDField(primary_key=True)
    sa_orm_sentinel = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        db_table = "revoked_auth_token"


class ScheduledNotification(models.Model):
    user = models.ForeignKey(AmiUser, models.DO_NOTHING)
    content_title = models.CharField()
    content_body = models.CharField()
    content_icon = models.CharField()
    sender = models.CharField()
    reference = models.CharField()
    scheduled_at = models.DateTimeField()
    sent_at = models.DateTimeField(blank=True, null=True)
    id = models.UUIDField(primary_key=True)
    sa_orm_sentinel = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        db_table = "scheduled_notification"
        unique_together = (("user", "reference"),)
