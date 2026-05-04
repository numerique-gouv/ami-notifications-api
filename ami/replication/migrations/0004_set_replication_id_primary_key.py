import uuid

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("replication", "0003_populate_replication_id"),
    ]

    operations = [
        migrations.AlterField(
            model_name="anonymizeduser",
            name="id",
            field=models.UUIDField(editable=False),
        ),
        migrations.AlterField(
            model_name="anonymizeduser",
            name="replication_id",
            field=models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False),
        ),
    ]
