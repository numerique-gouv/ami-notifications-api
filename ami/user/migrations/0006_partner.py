from django.db import migrations


def forward(apps, schema_editor):
    Consent = apps.get_model("user", "Consent")
    Partner = apps.get_model("partner", "Partner")
    for partner in Partner.objects.all():
        Consent.objects.filter(partner_slug=partner.slug).update(partner=partner)


class Migration(migrations.Migration):
    dependencies = [
        ("user", "0005_partner"),
    ]

    operations = [
        migrations.RunPython(forward, reverse_code=migrations.RunPython.noop),
    ]
