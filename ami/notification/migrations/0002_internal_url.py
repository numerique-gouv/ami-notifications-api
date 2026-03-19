from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("notification", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="schedulednotification",
            name="internal_url",
            field=models.CharField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="notification",
            name="internal_url",
            field=models.CharField(blank=True, null=True),
        ),
    ]
