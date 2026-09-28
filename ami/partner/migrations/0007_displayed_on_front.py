from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("partner", "0006_partner"),
    ]

    operations = [
        migrations.AddField(
            model_name="partner",
            name="displayed_on_front",
            field=models.BooleanField(default=True),
        ),
    ]
