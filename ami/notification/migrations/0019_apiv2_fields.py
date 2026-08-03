from django.db import migrations

sql_event_date = """
DROP TRIGGER IF EXISTS sync_event_date_tgr ON notification;
DROP FUNCTION IF EXISTS sync_event_date_func();

ALTER TABLE notification DROP COLUMN IF EXISTS send_date;
"""

sql_content_link = """
DROP TRIGGER IF EXISTS sync_content_link_tgr ON notification;
DROP FUNCTION IF EXISTS sync_content_link_func();

ALTER TABLE notification DROP COLUMN IF EXISTS item_external_url;
"""


class Migration(migrations.Migration):
    dependencies = [
        ("notification", "0018_content_subheading"),
    ]

    operations = [
        migrations.RunSQL(sql=sql_event_date, reverse_sql=migrations.RunSQL.noop),
        migrations.RunSQL(sql=sql_content_link, reverse_sql=migrations.RunSQL.noop),
    ]
