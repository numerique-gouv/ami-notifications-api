import uuid

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="AnonymizedUser",
            fields=[
                (
                    "replication_id",
                    models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False),
                ),
                ("id", models.UUIDField(editable=False)),
                ("last_logged_in", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField()),
                ("updated_at", models.DateTimeField()),
            ],
            options={
                "db_table": "ami_user_anonymized",
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="AnonymizedNotification",
            fields=[
                (
                    "replication_id",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True, serialize=False
                    ),
                ),
                ("id", models.UUIDField(editable=False)),
                ("content_title", models.CharField()),
                ("content_body", models.CharField()),
                ("content_icon", models.CharField(blank=True, null=True)),
                ("item_type", models.CharField(blank=True, null=True)),
                ("item_id", models.CharField(blank=True, null=True)),
                ("item_status_label", models.CharField(blank=True, null=True)),
                ("item_generic_status", models.CharField(blank=True, null=True)),
                ("item_canal", models.CharField(blank=True, null=True)),
                ("item_milestone_start_date", models.DateTimeField(blank=True, null=True)),
                ("item_milestone_end_date", models.DateTimeField(blank=True, null=True)),
                ("item_external_url", models.CharField(blank=True, null=True)),
                ("send_status", models.BooleanField(blank=True, null=True)),
                ("partner_id", models.CharField()),
                ("internal_url", models.CharField(blank=True, null=True)),
                ("read", models.BooleanField(default=False)),
                ("send_date", models.DateTimeField(default=django.utils.timezone.now)),
                ("try_push", models.BooleanField(blank=True, null=True)),
                ("created_at", models.DateTimeField()),
                ("updated_at", models.DateTimeField()),
            ],
            options={
                "db_table": "ami_notification_anonymized",
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="AnonymizedRegistration",
            fields=[
                (
                    "replication_id",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True, serialize=False
                    ),
                ),
                ("id", models.UUIDField(editable=False)),
                ("created_at", models.DateTimeField()),
                ("updated_at", models.DateTimeField()),
            ],
            options={
                "db_table": "ami_registration_anonymized",
                "abstract": False,
            },
        ),
    ]
