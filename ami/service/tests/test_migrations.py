import uuid

import pytest
from django.db import connection
from django.utils.timezone import now

from ami.partner.models import Partner


@pytest.mark.django_db()
def test_partner_uuid_migration(app, partner: Partner, partner_psl: Partner):
    def insert_service(cursor, service_id, field, value):
        cursor.execute(
            f"""
    INSERT INTO service_service (
      id,
      item_type,
      kind,
      title,
      short_description,
      description,
      url,
      icon,
      with_silent_login,
      restricted_to,
      created_at,
      updated_at,
      {field}
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            [
                service_id,
                str(service_id),
                "",
                "",
                "",
                "",
                "",
                "",
                False,
                "",
                now(),
                now(),
                value,
            ],
        )

    # test with old code
    with connection.cursor() as cursor:
        # insert
        service_id = uuid.uuid4()
        insert_service(cursor, service_id, "partner_id", partner_psl.slug)
        cursor.execute(
            "SELECT partner_id, partner_uuid FROM service_service WHERE id = %s", [service_id]
        )
        rows = cursor.fetchall()
        assert rows[0] == (partner_psl.slug, partner_psl.id)
        # update
        cursor.execute(
            "UPDATE service_service SET partner_id = %s WHERE id = %s",
            [
                partner.slug,
                service_id,
            ],
        )
        cursor.execute(
            "SELECT partner_id, partner_uuid FROM service_service WHERE id = %s", [service_id]
        )
        rows = cursor.fetchall()
        assert rows[0] == (partner.slug, partner.id)
    # test with new code
    with connection.cursor() as cursor:
        # insert
        service_id = uuid.uuid4()
        insert_service(cursor, service_id, "partner_uuid", partner_psl.id)
        cursor.execute(
            "SELECT partner_id, partner_uuid FROM service_service WHERE id = %s", [service_id]
        )
        rows = cursor.fetchall()
        assert rows[0] == (partner_psl.slug, partner_psl.id)
        # update
        cursor.execute(
            "UPDATE service_service SET partner_uuid = %s WHERE id = %s",
            [
                partner.id,
                service_id,
            ],
        )
        cursor.execute(
            "SELECT partner_id, partner_uuid FROM service_service WHERE id = %s", [service_id]
        )
        rows = cursor.fetchall()
        assert rows[0] == (partner.slug, partner.id)
