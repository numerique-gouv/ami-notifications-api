import django.db.models.deletion
from django.db import migrations, models

sql_partner_uuid = """
CREATE OR REPLACE FUNCTION sync_notification_partner_uuid_func()
  RETURNS TRIGGER AS $$
  BEGIN
    IF TG_OP = 'INSERT' THEN
      IF NEW.partner_uuid IS NULL AND NEW.partner_id IS NOT NULL THEN
        SELECT p.id
        INTO NEW.partner_uuid
        FROM partner_partner as p
        WHERE p.slug = NEW.partner_id;
      ELSIF NEW.partner_id IS NULL AND NEW.partner_uuid IS NOT NULL THEN
        SELECT p.slug
        INTO NEW.partner_id
        FROM partner_partner as p
        WHERE p.id = NEW.partner_uuid;
      END IF;
    ELSIF TG_OP = 'UPDATE' THEN
      IF NEW.partner_id IS DISTINCT FROM OLD.partner_id THEN
        SELECT p.id
        INTO NEW.partner_uuid
        FROM partner_partner as p
        WHERE p.slug = NEW.partner_id;
      ELSIF NEW.partner_uuid IS DISTINCT FROM OLD.partner_uuid THEN
        NEW.partner_id := NEW.partner_uuid;
        SELECT p.slug
        INTO NEW.partner_id
        FROM partner_partner as p
        WHERE p.id = NEW.partner_uuid;
      END IF;
    END IF;
    RETURN NEW;
  END;
$$ LANGUAGE plpgsql;
DROP TRIGGER IF EXISTS sync_notification_partner_uuid_tgr ON notification;
CREATE TRIGGER sync_notification_partner_uuid_tgr
 BEFORE INSERT OR UPDATE ON notification
 FOR EACH ROW EXECUTE FUNCTION sync_notification_partner_uuid_func();
"""
reverse_sql_partner_uuid = """
DROP TRIGGER IF EXISTS sync_notification_partner_uuid_tgr ON notification;
DROP FUNCTION IF EXISTS sync_notification_partner_uuid_func();
"""


sql_item_parent_partner_uuid = """
CREATE OR REPLACE FUNCTION sync_notification_item_parent_partner_uuid_func()
  RETURNS TRIGGER AS $$
  BEGIN
    IF TG_OP = 'INSERT' THEN
      IF NEW.item_parent_partner_uuid IS NULL AND NEW.item_parent_partner_id IS NOT NULL AND NEW.item_parent_partner_id != '' THEN
        SELECT p.id
        INTO NEW.item_parent_partner_uuid
        FROM partner_partner as p
        WHERE p.slug = NEW.item_parent_partner_id;
      ELSIF NEW.item_parent_partner_id IS NULL AND NEW.item_parent_partner_uuid IS NOT NULL THEN
        SELECT p.slug
        INTO NEW.item_parent_partner_id
        FROM partner_partner as p
        WHERE p.id = NEW.item_parent_partner_uuid;
      END IF;
    ELSIF TG_OP = 'UPDATE' THEN
      IF NEW.item_parent_partner_id IS DISTINCT FROM OLD.item_parent_partner_id THEN
        IF NEW.item_parent_partner_id IS NOT NULL AND NEW.item_parent_partner_id != '' THEN
          SELECT p.id
          INTO NEW.item_parent_partner_uuid
          FROM partner_partner as p
          WHERE p.slug = NEW.item_parent_partner_id;
        ELSE
          NEW.item_parent_partner_uuid = null;
        END IF;
      ELSIF NEW.item_parent_partner_uuid IS DISTINCT FROM OLD.item_parent_partner_uuid THEN
        IF NEW.item_parent_partner_uuid IS NOT NULL THEN
          SELECT p.slug
          INTO NEW.item_parent_partner_id
          FROM partner_partner as p
          WHERE p.id = NEW.item_parent_partner_uuid;
        ELSE
          NEW.item_parent_partner_id = null;
        END IF;
      END IF;
    END IF;
    RETURN NEW;
  END;
$$ LANGUAGE plpgsql;
DROP TRIGGER IF EXISTS sync_notification_item_parent_partner_uuid_tgr ON notification;
CREATE TRIGGER sync_notification_item_parent_partner_uuid_tgr
 BEFORE INSERT OR UPDATE ON notification
 FOR EACH ROW EXECUTE FUNCTION sync_notification_item_parent_partner_uuid_func();
"""
reverse_sql_item_parent_partner_uuid = """
DROP TRIGGER IF EXISTS sync_notification_item_parent_partner_uuid_tgr ON notification;
DROP FUNCTION IF EXISTS sync_notification_item_parent_partner_uuid_func();
"""


class Migration(migrations.Migration):
    dependencies = [
        ("notification", "0021_partner"),
        ("partner", "0003_partner"),
    ]

    operations = [
        migrations.AddField(
            model_name="notification",
            name="item_parent_partner",
            field=models.ForeignKey(
                db_column="item_parent_partner_uuid",
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="parent_notifications",
                to="partner.partner",
            ),
        ),
        migrations.AddField(
            model_name="notification",
            name="partner",
            field=models.ForeignKey(
                db_column="partner_uuid",
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="notifications",
                to="partner.partner",
            ),
        ),
        migrations.AlterField(
            model_name="notification",
            name="partner_slug",
            field=models.CharField(db_column="partner_id", null=True),
        ),
        migrations.RunSQL(sql=sql_partner_uuid, reverse_sql=reverse_sql_partner_uuid),
        migrations.RunSQL(
            sql=sql_item_parent_partner_uuid, reverse_sql=reverse_sql_item_parent_partner_uuid
        ),
    ]
