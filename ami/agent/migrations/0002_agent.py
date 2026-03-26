import uuid

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("agent", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Agent",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True, serialize=False
                    ),
                ),
                ("proconnect_sub", models.CharField(max_length=255, unique=True)),
                (
                    "role",
                    models.CharField(
                        choices=[
                            ("support", "Support"),
                            ("notifications", "Notifications"),
                            ("admin", "Admin"),
                        ],
                        max_length=20,
                        null=True,
                        blank=True,
                    ),
                ),
                ("proconnect_last_login", models.DateTimeField(null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL
                    ),
                ),
            ],
        ),
    ]
