import uuid

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("user", "0011_registration_deleted_at"),
    ]

    operations = [
        migrations.CreateModel(
            name="PersonalDataConsent",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True, serialize=False
                    ),
                ),
                ("consent_datetime", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "user",
                    models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to="user.user"),
                ),
            ],
            options={
                "db_table": "personal_data_consent",
                "unique_together": {("user",)},
            },
        ),
    ]
