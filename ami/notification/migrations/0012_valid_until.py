from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("notification", "0011_remove_content_private_body_from_ScheduledNotification"),
    ]

    operations = [
        migrations.AddField(
            model_name="notification",
            name="valid_until",
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
