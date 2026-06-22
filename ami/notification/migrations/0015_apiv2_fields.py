import django.utils.timezone
from django.db import migrations, models

sql_event_date = """
CREATE OR REPLACE FUNCTION sync_event_date_func()
  RETURNS TRIGGER AS $$
  BEGIN
    IF TG_OP = 'INSERT' THEN
      IF NEW.event_date IS NULL AND NEW.send_date IS NOT NULL THEN
        NEW.event_date := NEW.send_date;
      ELSIF NEW.send_date IS NULL AND NEW.event_date IS NOT NULL THEN
        NEW.send_date := NEW.event_date;
      END IF;

    ELSIF TG_OP = 'UPDATE' THEN
      IF NEW.event_date IS DISTINCT FROM OLD.event_date THEN
        NEW.send_date := NEW.event_date;
      ELSIF NEW.send_date IS DISTINCT FROM OLD.send_date THEN
        NEW.event_date := NEW.send_date;
      END IF;
    END IF;

    RETURN NEW;
  END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS sync_event_date_tgr ON notification;
CREATE TRIGGER sync_event_date_tgr
 BEFORE INSERT OR UPDATE ON notification
 FOR EACH ROW EXECUTE FUNCTION sync_event_date_func();
"""

reverse_sql_event_date = """
DROP TRIGGER IF EXISTS sync_event_date_tgr ON notification;
DROP FUNCTION IF EXISTS sync_event_date_func();
"""


sql_content_link = """
CREATE OR REPLACE FUNCTION sync_content_link_func()
  RETURNS TRIGGER AS $$
  BEGIN
    IF TG_OP = 'INSERT' THEN
      IF NEW.content_link IS NULL AND NEW.item_external_url IS NOT NULL THEN
        NEW.content_link := NEW.item_external_url;
      ELSIF NEW.item_external_url IS NULL AND NEW.content_link IS NOT NULL THEN
        NEW.item_external_url := NEW.content_link;
      END IF;

    ELSIF TG_OP = 'UPDATE' THEN
      IF NEW.content_link IS DISTINCT FROM OLD.content_link THEN
        NEW.item_external_url := NEW.content_link;
      ELSIF NEW.item_external_url IS DISTINCT FROM OLD.item_external_url THEN
        NEW.content_link := NEW.item_external_url;
      END IF;
    END IF;

    RETURN NEW;
  END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS sync_content_link_tgr ON notification;
CREATE TRIGGER sync_content_link_tgr
 BEFORE INSERT OR UPDATE ON notification
 FOR EACH ROW EXECUTE FUNCTION sync_content_link_func();
"""

reverse_sql_content_link = """
DROP TRIGGER IF EXISTS sync_content_link_tgr ON notification;
DROP FUNCTION IF EXISTS sync_content_link_func();
"""


class Migration(migrations.Migration):
    dependencies = [
        ("notification", "0014_content_icon"),
    ]

    operations = [
        migrations.AddField(
            model_name="notification",
            name="content_link",
            field=models.CharField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="notification",
            name="event_date",
            field=models.DateTimeField(null=True),
        ),
        migrations.AlterField(
            model_name="notification",
            name="send_date",
            field=models.DateTimeField(default=django.utils.timezone.now, null=True),
        ),
        migrations.AddField(
            model_name="notification",
            name="item_parent_id",
            field=models.CharField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="notification",
            name="item_parent_partner_id",
            field=models.CharField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="notification",
            name="item_parent_type",
            field=models.CharField(blank=True, null=True),
        ),
        migrations.RunSQL(sql=sql_event_date, reverse_sql=reverse_sql_event_date),
        migrations.RunSQL(sql=sql_content_link, reverse_sql=reverse_sql_content_link),
    ]
