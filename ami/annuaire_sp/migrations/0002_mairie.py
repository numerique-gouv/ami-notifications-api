import uuid

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("annuaire_sp", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Mairie",
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
                ("code_insee_commune", models.CharField(unique=True)),
                ("id_service_local", models.CharField()),
                ("nom", models.CharField()),
                ("url_service_public", models.CharField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
