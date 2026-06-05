from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("notification", "0012_valid_until"),
    ]

    operations = [
        migrations.AddField(
            model_name="notification",
            name="item_is_archived",
            field=models.BooleanField(null=True),
        ),
    ]
