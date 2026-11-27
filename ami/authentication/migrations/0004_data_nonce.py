import uuid

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("authentication", "0003_token_context"),
        ("user", "0013_user_fc_sub"),
    ]

    operations = [
        migrations.CreateModel(
            name="DataNonce",
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
                ("nonce", models.CharField(max_length=256)),
                ("context", models.JSONField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "user",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="user.user"),
                ),
            ],
            options={
                "db_table": "data_nonce",
            },
        ),
    ]
