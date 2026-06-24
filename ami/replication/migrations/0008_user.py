from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("replication", "0007_anonymizedregistration_subscription"),
    ]

    operations = [
        migrations.AddField(
            model_name="anonymizednotification",
            name="user_id",
            field=models.UUIDField(db_index=True, null=True),
        ),
        migrations.AddField(
            model_name="anonymizedregistration",
            name="user_id",
            field=models.UUIDField(db_index=True, null=True),
        ),
    ]
