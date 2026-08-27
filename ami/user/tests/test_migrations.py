import uuid

import pytest
from django.db import connection
from django.utils.timezone import now

from ami.partner.models import Partner


@pytest.mark.django_db()
def test_partner_uuid_migration(app, two_users, partner: Partner, partner_psl: Partner):
    def insert_consent(cursor, consent_id, user_id, field, value):
        cursor.execute(
            f"""
    INSERT INTO consent (
      id,
      user_id,
      created_at,
      updated_at,
      {field}
    ) VALUES (%s, %s, %s, %s, %s)""",
            [
                consent_id,
                user_id,
                now(),
                now(),
                value,
            ],
        )

    # test with old code
    with connection.cursor() as cursor:
        # insert
        consent_id = uuid.uuid4()
        insert_consent(cursor, consent_id, two_users[0].id, "partner_id", partner_psl.slug)
        cursor.execute("SELECT partner_id, partner_uuid FROM consent WHERE id = %s", [consent_id])
        rows = cursor.fetchall()
        assert rows[0] == (partner_psl.slug, partner_psl.id)
        # update
        cursor.execute(
            "UPDATE consent SET partner_id = %s WHERE id = %s",
            [
                partner.slug,
                consent_id,
            ],
        )
        cursor.execute("SELECT partner_id, partner_uuid FROM consent WHERE id = %s", [consent_id])
        rows = cursor.fetchall()
        assert rows[0] == (partner.slug, partner.id)
    # test with new code
    with connection.cursor() as cursor:
        # insert
        consent_id = uuid.uuid4()
        insert_consent(cursor, consent_id, two_users[1].id, "partner_uuid", partner_psl.id)
        cursor.execute("SELECT partner_id, partner_uuid FROM consent WHERE id = %s", [consent_id])
        rows = cursor.fetchall()
        assert rows[0] == (partner_psl.slug, partner_psl.id)
        # update
        cursor.execute(
            "UPDATE consent SET partner_uuid = %s WHERE id = %s",
            [
                partner.id,
                consent_id,
            ],
        )
        cursor.execute("SELECT partner_id, partner_uuid FROM consent WHERE id = %s", [consent_id])
        rows = cursor.fetchall()
        assert rows[0] == (partner.slug, partner.id)
