import uuid

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("user", "0002_remove_sa_orm_sentinel"),
    ]

    operations = [
        migrations.CreateModel(
            name="Consent",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True, serialize=False
                    ),
                ),
                ("partner_id", models.CharField(max_length=100)),
                ("consent_datetime", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "user",
                    models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to="user.user"),
                ),
            ],
            options={
                "db_table": "consent",
                "unique_together": {("user", "partner_id")},
            },
        ),
    ]
