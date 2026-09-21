from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("notification", "0024_partner"),
        ("partner", "0006_partner"),
        ("user", "0009_device_id"),
    ]

    operations = [
        # recreate index on user_id, as a foreign key it should already be there but
        # old databases may be missing it.
        # 1002fc38 is names_digest("notification", "user_id", length=8) (as done in
        # django _create_index_name() method).
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS notification_user_id_1002fc38 ON notification(user_id)",
            "",
        ),
        # ditto for scheduled_notification
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS scheduled_notification_user_id_89882ede ON scheduled_notification(user_id)",
            "",
        ),
    ]
