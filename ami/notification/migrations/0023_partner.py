from django.db import migrations


def forward(apps, schema_editor):
    Notification = apps.get_model("notification", "Notification")
    Partner = apps.get_model("partner", "Partner")
    for partner in Partner.objects.all():
        Notification.objects.filter(partner_slug=partner.slug).update(partner=partner)
        Notification.objects.filter(item_parent_partner_slug=partner.slug).update(
            item_parent_partner=partner
        )


class Migration(migrations.Migration):
    dependencies = [
        ("notification", "0022_partner"),
    ]

    operations = [
        migrations.RunPython(forward, reverse_code=migrations.RunPython.noop),
    ]
