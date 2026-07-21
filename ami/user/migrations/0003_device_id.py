from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("user", "0002_remove_sa_orm_sentinel"),
    ]

    operations = [
        migrations.AddField(
            model_name="registration",
            name="device_id",
            field=models.CharField(blank=True, null=True),
        ),
    ]
