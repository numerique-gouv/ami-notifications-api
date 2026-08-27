from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("replication", "0010_content_subheading"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="anonymizednotification",
            name="item_parent_partner_id",
        ),
        migrations.RemoveField(
            model_name="anonymizednotification",
            name="partner_id",
        ),
    ]
