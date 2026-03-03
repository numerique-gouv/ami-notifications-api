import uuid

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("user", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Notification",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("content_body", models.CharField()),
                ("sender", models.CharField()),
                ("content_title", models.CharField()),
                ("sa_orm_sentinel", models.IntegerField(blank=True, null=True)),
                ("content_icon", models.CharField(blank=True, null=True)),
                ("item_type", models.CharField(blank=True, null=True)),
                ("item_id", models.CharField(blank=True, null=True)),
                ("item_status_label", models.CharField(blank=True, null=True)),
                ("item_generic_status", models.CharField(blank=True, null=True)),
                ("item_canal", models.CharField(blank=True, null=True)),
                (
                    "item_milestone_start_date",
                    models.DateTimeField(blank=True, null=True),
                ),
                (
                    "item_milestone_end_date",
                    models.DateTimeField(blank=True, null=True),
                ),
                ("item_external_url", models.CharField(blank=True, null=True)),
                ("send_date", models.DateTimeField(default=django.utils.timezone.now)),
                ("read", models.BooleanField(default=False)),
                ("try_push", models.BooleanField(blank=True, null=True)),
                ("send_status", models.BooleanField(blank=True, null=True)),
                ("partner_id", models.CharField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "user",
                    models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to="user.user"),
                ),
            ],
            options={
                "db_table": "notification",
            },
        ),
        migrations.CreateModel(
            name="ScheduledNotification",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("content_title", models.CharField()),
                ("content_body", models.CharField()),
                ("content_icon", models.CharField()),
                ("sender", models.CharField()),
                ("reference", models.CharField()),
                ("scheduled_at", models.DateTimeField()),
                ("sent_at", models.DateTimeField(blank=True, null=True)),
                ("sa_orm_sentinel", models.IntegerField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "user",
                    models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to="user.user"),
                ),
            ],
            options={
                "db_table": "scheduled_notification",
                "unique_together": {("user", "reference")},
            },
        ),
    ]
