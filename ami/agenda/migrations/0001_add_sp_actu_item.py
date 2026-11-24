import uuid

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="SpActuItem",
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
                ("external_id", models.CharField(unique=True)),
                ("title", models.CharField()),
                ("date", models.DateField(null=True)),
                ("start_date", models.DateField(null=True)),
                ("end_date", models.DateField(null=True)),
                (
                    "themes",
                    django.contrib.postgres.fields.ArrayField(
                        base_field=models.CharField(blank=True, max_length=100),
                        null=True,
                    ),
                ),
                ("url", models.CharField()),
                ("initial_publication_date", models.DateField()),
                ("last_update_date", models.DateField(null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
