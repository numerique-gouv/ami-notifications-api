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
            name="AuditEntry",
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
                ("author_first_name", models.CharField(max_length=150)),
                ("author_last_name", models.CharField(max_length=150)),
                ("author_email", models.EmailField(max_length=254)),
                ("author_proconnect_sub", models.CharField(max_length=255)),
                ("action_type", models.CharField(max_length=100, db_index=True)),
                ("action_code", models.CharField(max_length=100, db_index=True)),
                ("extra_data", models.JSONField(blank=True, default=dict)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "author",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="agent.agent",
                    ),
                ),
            ],
            options={
                "ordering": ["-created_at"],
            },
        ),
    ]
