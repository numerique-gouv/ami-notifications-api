import uuid

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("fi", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="FISession",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True, serialize=False
                    ),
                ),
                ("user_data", models.JSONField()),
                ("state", models.CharField(max_length=256)),
                ("nonce", models.CharField(max_length=256)),
                ("code", models.CharField(max_length=256)),
                ("access_token", models.CharField(max_length=256)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
