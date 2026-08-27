import django.db.models.deletion
from django.db import migrations, models

sql_partner_uuid = """
CREATE OR REPLACE FUNCTION sync_service_partner_uuid_func()
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
        SELECT p.slug
        INTO NEW.partner_id
        FROM partner_partner as p
        WHERE p.id = NEW.partner_uuid;
      END IF;
    END IF;
    RETURN NEW;
  END;
$$ LANGUAGE plpgsql;
DROP TRIGGER IF EXISTS sync_service_partner_uuid_tgr ON service_service;
CREATE TRIGGER sync_service_partner_uuid_tgr
 BEFORE INSERT OR UPDATE ON service_service
 FOR EACH ROW EXECUTE FUNCTION sync_service_partner_uuid_func();
"""
reverse_sql_partner_uuid = """
DROP TRIGGER IF EXISTS sync_service_partner_uuid_tgr ON service_service;
DROP FUNCTION IF EXISTS sync_service_partner_uuid_func();
"""


class Migration(migrations.Migration):
    dependencies = [
        ("partner", "0003_partner"),
        ("service", "0008_partner"),
    ]

    operations = [
        migrations.AddField(
            model_name="service",
            name="partner",
            field=models.ForeignKey(
                db_column="partner_uuid",
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="services",
                to="partner.partner",
            ),
        ),
        migrations.AlterField(
            model_name="service",
            name="partner_slug",
            field=models.CharField(
                choices=[
                    ("psl", "PSL"),
                    ("dinum-dn", "demarche.numerique.gouv.fr"),
                    ("dinum-ami", "AMI"),
                    ("dinum-rdvsp", "RDV SP"),
                ],
                db_column="partner_id",
                null=True,
            ),
        ),
        migrations.RunSQL(sql=sql_partner_uuid, reverse_sql=reverse_sql_partner_uuid),
    ]
