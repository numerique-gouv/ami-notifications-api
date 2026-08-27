from django.db import migrations


def forward(apps, schema_editor):
    Partner = apps.get_model("partner", "Partner")
    Partner.objects.create(
        slug="psl",
        name="Service Public",
        icon="",
        consent_is_enabled=False,
    )
    Partner.objects.create(
        slug="dinum-dn",
        name="Démarche Numérique",
        icon="fr-icon-infinity-line",
        consent_is_enabled=True,
    )
    Partner.objects.create(
        slug="dinum-ami",
        name="AMI",
        icon="fr-icon-smartphone-line",
        consent_is_enabled=True,
    )
    Partner.objects.create(
        slug="dinum-rdvsp",
        name="Rendez-vous SP",
        icon="",
        consent_is_enabled=True,
    )


class Migration(migrations.Migration):
    dependencies = [
        ("partner", "0002_partner"),
    ]

    operations = [
        migrations.RunPython(forward, reverse_code=migrations.RunPython.noop),
    ]
