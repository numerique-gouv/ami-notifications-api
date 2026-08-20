from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("service", "0005_service_kind"),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name="service",
            unique_together={("kind", "partner_id", "item_type")},
        ),
    ]
