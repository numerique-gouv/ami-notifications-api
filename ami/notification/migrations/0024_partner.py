import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("notification", "0023_partner"),
    ]

    operations = [
        migrations.AlterField(
            model_name="notification",
            name="partner",
            field=models.ForeignKey(
                db_column="partner_uuid",
                on_delete=django.db.models.deletion.PROTECT,
                related_name="notifications",
                to="partner.partner",
            ),
        ),
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.RemoveField(
                    model_name="notification",
                    name="item_parent_partner_slug",
                ),
            ]
        ),
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.RemoveField(
                    model_name="notification",
                    name="partner_slug",
                ),
            ]
        ),
    ]
