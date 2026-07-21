from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("replication", "0010_content_subheading"),
    ]

    operations = [
        migrations.AddField(
            model_name="anonymizeduser",
            name="consent_datetime",
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
