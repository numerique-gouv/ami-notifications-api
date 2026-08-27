import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("partner", "0003_partner"),
        ("user", "0006_partner"),
    ]

    operations = [
        migrations.AlterField(
            model_name="consent",
            name="partner",
            field=models.ForeignKey(
                db_column="partner_uuid",
                on_delete=django.db.models.deletion.PROTECT,
                related_name="consents",
                to="partner.partner",
            ),
        ),
        migrations.AlterUniqueTogether(
            name="consent",
            unique_together={("user", "partner")},
        ),
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.RemoveField(
                    model_name="consent",
                    name="partner_slug",
                ),
            ]
        ),
    ]
