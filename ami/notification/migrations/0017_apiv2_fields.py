import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("notification", "0016_apiv2_fields"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.RemoveField(
                    model_name="notification",
                    name="item_external_url",
                ),
            ],
            database_operations=[],
        ),
        migrations.AlterField(
            model_name="notification",
            name="event_date",
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.RemoveField(
                    model_name="notification",
                    name="send_date",
                ),
            ],
            database_operations=[],
        ),
    ]
