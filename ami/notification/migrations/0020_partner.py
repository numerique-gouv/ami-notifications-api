from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("notification", "0019_apiv2_fields"),
    ]

    operations = [
        migrations.AlterField(
            model_name="notification",
            name="item_parent_partner_id",
            field=models.CharField(blank=True, db_column="item_parent_partner_id", null=True),
        ),
        migrations.RenameField(
            model_name="notification",
            old_name="item_parent_partner_id",
            new_name="item_parent_partner_slug",
        ),
        migrations.AlterField(
            model_name="notification",
            name="partner_id",
            field=models.CharField(db_column="partner_id"),
        ),
        migrations.RenameField(
            model_name="notification",
            old_name="partner_id",
            new_name="partner_slug",
        ),
    ]
