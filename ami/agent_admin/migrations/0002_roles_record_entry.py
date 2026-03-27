import uuid

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("agent", "0002_agent"),
        ("agent_admin", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="RolesRecordEntry",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True, serialize=False
                    ),
                ),
                (
                    "new_role",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("support", "Support"),
                            ("notifications", "Notifications"),
                            ("admin", "Admin"),
                        ],
                        max_length=20,
                        null=True,
                    ),
                ),
                (
                    "old_role",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("support", "Support"),
                            ("notifications", "Notifications"),
                            ("admin", "Admin"),
                        ],
                        max_length=20,
                        null=True,
                    ),
                ),
                ("update_date", models.DateTimeField(null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "admin_agent",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="roles_as_admin_agent",
                        to="agent.agent",
                    ),
                ),
                (
                    "updated_agent",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="roles_as_updated_agent",
                        to="agent.agent",
                    ),
                ),
            ],
        ),
    ]
