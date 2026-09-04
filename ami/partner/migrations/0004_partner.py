from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("partner", "0003_partner"),
    ]

    operations = [
        migrations.AddField(
            model_name="partner",
            name="link",
            field=models.CharField(blank=True),
        ),
    ]
