import uuid

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("partner", "0006_partner"),
    ]

    operations = [
        migrations.CreateModel(
            name="CheckList",
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
                ("icon", models.CharField(blank=True)),
                ("definition", models.JSONField(default=dict)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "partner",
                    models.ForeignKey(
                        db_column="partner_uuid",
                        on_delete=django.db.models.deletion.PROTECT,
                        to="partner.partner",
                    ),
                ),
            ],
        ),
    ]
