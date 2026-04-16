from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("notification", "0008_partner_id"),
    ]

    operations = [
        migrations.AlterField(
            model_name="notification",
            name="partner_id",
            field=models.CharField(),
        ),
    ]
