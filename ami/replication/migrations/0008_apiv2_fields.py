from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("replication", "0007_anonymizedregistration_subscription"),
    ]

    operations = [
        migrations.RenameField(
            model_name="anonymizednotification",
            old_name="item_external_url",
            new_name="content_link",
        ),
        migrations.RenameField(
            model_name="anonymizednotification",
            old_name="send_date",
            new_name="event_date",
        ),
        migrations.AddField(
            model_name="anonymizednotification",
            name="item_parent_id",
            field=models.CharField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="anonymizednotification",
            name="item_parent_partner_id",
            field=models.CharField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="anonymizednotification",
            name="item_parent_type",
            field=models.CharField(blank=True, null=True),
        ),
    ]
