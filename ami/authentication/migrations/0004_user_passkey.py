import uuid

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("authentication", "0003_token_context"),
        ("user", "0002_remove_sa_orm_sentinel"),
    ]

    operations = [
        migrations.CreateModel(
            name="UserPasskey",
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
                ("credential_id", models.CharField()),
                ("credential_public_key", models.CharField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "user",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="user.user"),
                ),
            ],
        ),
    ]
