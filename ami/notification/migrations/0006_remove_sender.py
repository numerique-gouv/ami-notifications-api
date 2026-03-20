from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("notification", "0005_remove_sender"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="notification",
            name="sender",
        ),
        migrations.RemoveField(
            model_name="schedulednotification",
            name="sender",
        ),
    ]
