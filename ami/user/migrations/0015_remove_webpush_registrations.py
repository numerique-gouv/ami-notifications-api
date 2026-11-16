from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("user", "0014_remove_webpush_registrations"),
    ]

    operations = [
        migrations.AlterField(
            model_name="registration",
            name="device_id",
            field=models.CharField(blank=True),
        ),
        migrations.AlterField(
            model_name="registration",
            name="subscription",
            field=models.JSONField(blank=True, default=dict),
        ),
    ]
