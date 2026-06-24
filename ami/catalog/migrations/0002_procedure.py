import uuid

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("catalog", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Procedure",
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
                ("partner_id", models.CharField()),
                ("external_item_type", models.CharField()),
                ("title", models.CharField()),
                ("short_description", models.TextField()),
                ("description", models.TextField()),
                ("external_url", models.TextField()),
                ("with_silent_login", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "unique_together": {("partner_id", "external_item_type")},
            },
        ),
    ]
