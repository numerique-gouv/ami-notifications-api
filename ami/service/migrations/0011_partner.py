import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("partner", "0003_partner"),
        ("service", "0010_partner"),
    ]

    operations = [
        migrations.AlterField(
            model_name="service",
            name="partner",
            field=models.ForeignKey(
                db_column="partner_uuid",
                on_delete=django.db.models.deletion.PROTECT,
                related_name="services",
                to="partner.partner",
            ),
        ),
        migrations.AlterUniqueTogether(
            name="service",
            unique_together={("kind", "partner", "item_type")},
        ),
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.RemoveField(
                    model_name="service",
                    name="partner_slug",
                ),
            ],
            database_operations=[],
        ),
    ]
