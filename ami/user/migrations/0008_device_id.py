from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("user", "0007_partner"),
    ]

    operations = [
        migrations.AddField(
            model_name="registration",
            name="device_id",
            field=models.CharField(blank=True, null=True),
        ),
    ]
