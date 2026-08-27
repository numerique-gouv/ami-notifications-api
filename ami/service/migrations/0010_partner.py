from django.db import migrations


def forward(apps, schema_editor):
    Service = apps.get_model("service", "Service")
    Partner = apps.get_model("partner", "Partner")
    for partner in Partner.objects.all():
        Service.objects.filter(partner_slug=partner.slug).update(partner=partner)


class Migration(migrations.Migration):
    dependencies = [
        ("service", "0009_partner"),
    ]

    operations = [
        migrations.RunPython(forward, reverse_code=migrations.RunPython.noop),
    ]
