from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("replication", "0012_partner"),
    ]

    operations = [
        migrations.AddField(
            model_name="anonymizedregistration",
            name="deleted_at",
            field=models.DateTimeField(null=True),
        ),
    ]
