from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("replication", "0011_partner"),
    ]

    operations = [
        migrations.AddField(
            model_name="anonymizednotification",
            name="item_parent_partner_id",
            field=models.UUIDField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="anonymizednotification",
            name="partner_id",
            field=models.UUIDField(null=True),
        ),
    ]
