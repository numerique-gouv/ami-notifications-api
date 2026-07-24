import uuid

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("service", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Service",
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
                (
                    "partner_id",
                    models.CharField(
                        choices=[
                            ("psl", "PSL"),
                            ("dinum-dn", "demarche.numerique.gouv.fr"),
                            ("dinum-ami", "AMI"),
                        ]
                    ),
                ),
                ("item_type", models.CharField()),
                ("title", models.CharField()),
                ("short_description", models.TextField()),
                ("description", models.TextField()),
                ("url", models.TextField()),
                ("with_silent_login", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "unique_together": {("partner_id", "item_type")},
            },
        ),
    ]
