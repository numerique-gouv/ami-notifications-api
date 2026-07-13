from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("replication", "0009_apiv2_fields"),
    ]

    operations = [
        migrations.AddField(
            model_name="anonymizednotification",
            name="content_subheading",
            field=models.CharField(blank=True, null=True),
        ),
    ]
