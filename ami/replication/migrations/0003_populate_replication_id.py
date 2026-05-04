import uuid

from django.db import migrations


def gen_replication_id(apps, schema_editor):
    AnonymizedUser = apps.get_model("replication", "AnonymizedUser")
    for row in AnonymizedUser.objects.all():
        row.replication_id = uuid.uuid4()
        row.save(update_fields=["replication_id"])


class Migration(migrations.Migration):
    dependencies = [
        ("replication", "0002_remove_anonymizeduser_original_id_and_more"),
    ]

    operations = [
        migrations.RunPython(gen_replication_id, reverse_code=migrations.RunPython.noop),
    ]
