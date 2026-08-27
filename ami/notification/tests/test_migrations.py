import uuid

import pytest
from django.db import connection
from django.utils.timezone import now

from ami.partner.models import Partner


@pytest.mark.django_db()
def test_partner_uuid_migration(app, user, partner: Partner, partner_psl: Partner):
    def insert_notification(cursor, user_id, notification_id, field, value):
        cursor.execute(
            f"""
    INSERT INTO notification (
      id,
      user_id,
      content_body,
      content_title,
      read,
      event_date,
      created_at,
      updated_at,
      {field}
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            [
                notification_id,
                user_id,
                "",
                "",
                False,
                now(),
                now(),
                now(),
                value,
            ],
        )

    # test with old code
    with connection.cursor() as cursor:
        # insert
        notification_id = uuid.uuid4()
        insert_notification(cursor, user.id, notification_id, "partner_id", partner_psl.slug)
        cursor.execute(
            "SELECT partner_id, partner_uuid FROM notification WHERE id = %s", [notification_id]
        )
        rows = cursor.fetchall()
        assert rows[0] == (partner_psl.slug, partner_psl.id)
        # update
        cursor.execute(
            "UPDATE notification SET partner_id = %s WHERE id = %s",
            [
                partner.slug,
                notification_id,
            ],
        )
        cursor.execute(
            "SELECT partner_id, partner_uuid FROM notification WHERE id = %s", [notification_id]
        )
        rows = cursor.fetchall()
        assert rows[0] == (partner.slug, partner.id)
    # test with new code
    with connection.cursor() as cursor:
        # insert
        notification_id = uuid.uuid4()
        insert_notification(cursor, user.id, notification_id, "partner_uuid", partner_psl.id)
        cursor.execute(
            "SELECT partner_id, partner_uuid FROM notification WHERE id = %s", [notification_id]
        )
        rows = cursor.fetchall()
        assert rows[0] == (partner_psl.slug, partner_psl.id)
        # update
        cursor.execute(
            "UPDATE notification SET partner_uuid = %s WHERE id = %s",
            [
                partner.id,
                notification_id,
            ],
        )
        cursor.execute(
            "SELECT partner_id, partner_uuid FROM notification WHERE id = %s", [notification_id]
        )
        rows = cursor.fetchall()
        assert rows[0] == (partner.slug, partner.id)


@pytest.mark.django_db()
def test_item_parent_partner_uuid_migration(app, user, partner: Partner, partner_psl: Partner):
    def insert_notification(cursor, user_id, notification_id, field, value):
        cursor.execute(
            f"""
    INSERT INTO notification (
      id,
      user_id,
      partner_uuid,
      content_body,
      content_title,
      read,
      event_date,
      created_at,
      updated_at,
      {field}
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            [
                notification_id,
                user_id,
                partner_psl.id,
                "",
                "",
                False,
                now(),
                now(),
                now(),
                value,
            ],
        )

    # test with old code
    with connection.cursor() as cursor:
        # insert
        notification_id = uuid.uuid4()
        insert_notification(
            cursor, user.id, notification_id, "item_parent_partner_id", partner_psl.slug
        )
        cursor.execute(
            "SELECT item_parent_partner_id, item_parent_partner_uuid FROM notification WHERE id = %s",
            [notification_id],
        )
        rows = cursor.fetchall()
        assert rows[0] == (partner_psl.slug, partner_psl.id)
        # update
        cursor.execute(
            "UPDATE notification SET item_parent_partner_id = %s WHERE id = %s",
            [
                partner.slug,
                notification_id,
            ],
        )
        cursor.execute(
            "SELECT item_parent_partner_id, item_parent_partner_uuid FROM notification WHERE id = %s",
            [notification_id],
        )
        rows = cursor.fetchall()
        assert rows[0] == (partner.slug, partner.id)

        # insert with None value
        notification_id = uuid.uuid4()
        insert_notification(cursor, user.id, notification_id, "item_parent_partner_id", None)
        cursor.execute(
            "SELECT item_parent_partner_id, item_parent_partner_uuid FROM notification WHERE id = %s",
            [notification_id],
        )
        rows = cursor.fetchall()
        assert rows[0] == (None, None)
        # update
        cursor.execute(
            "UPDATE notification SET item_parent_partner_id = %s WHERE id = %s",
            [
                partner.slug,
                notification_id,
            ],
        )
        cursor.execute(
            "SELECT item_parent_partner_id, item_parent_partner_uuid FROM notification WHERE id = %s",
            [notification_id],
        )
        rows = cursor.fetchall()
        assert rows[0] == (partner.slug, partner.id)
        # update
        cursor.execute(
            "UPDATE notification SET item_parent_partner_id = %s WHERE id = %s",
            [
                None,
                notification_id,
            ],
        )
        cursor.execute(
            "SELECT item_parent_partner_id, item_parent_partner_uuid FROM notification WHERE id = %s",
            [notification_id],
        )
        rows = cursor.fetchall()
        assert rows[0] == (None, None)

        # insert with empty value
        notification_id = uuid.uuid4()
        insert_notification(cursor, user.id, notification_id, "item_parent_partner_id", "")
        cursor.execute(
            "SELECT item_parent_partner_id, item_parent_partner_uuid FROM notification WHERE id = %s",
            [notification_id],
        )
        rows = cursor.fetchall()
        assert rows[0] == ("", None)
        # update
        cursor.execute(
            "UPDATE notification SET item_parent_partner_id = %s WHERE id = %s",
            [
                partner.slug,
                notification_id,
            ],
        )
        cursor.execute(
            "SELECT item_parent_partner_id, item_parent_partner_uuid FROM notification WHERE id = %s",
            [notification_id],
        )
        rows = cursor.fetchall()
        assert rows[0] == (partner.slug, partner.id)
        # update
        cursor.execute(
            "UPDATE notification SET item_parent_partner_id = %s WHERE id = %s",
            [
                "",
                notification_id,
            ],
        )
        cursor.execute(
            "SELECT item_parent_partner_id, item_parent_partner_uuid FROM notification WHERE id = %s",
            [notification_id],
        )
        rows = cursor.fetchall()
        assert rows[0] == ("", None)
    # test with new code
    with connection.cursor() as cursor:
        # insert
        notification_id = uuid.uuid4()
        insert_notification(
            cursor, user.id, notification_id, "item_parent_partner_uuid", partner_psl.id
        )
        cursor.execute(
            "SELECT item_parent_partner_id, item_parent_partner_uuid FROM notification WHERE id = %s",
            [notification_id],
        )
        rows = cursor.fetchall()
        assert rows[0] == (partner_psl.slug, partner_psl.id)
        # update
        cursor.execute(
            "UPDATE notification SET item_parent_partner_uuid = %s WHERE id = %s",
            [
                partner.id,
                notification_id,
            ],
        )
        cursor.execute(
            "SELECT item_parent_partner_id, item_parent_partner_uuid FROM notification WHERE id = %s",
            [notification_id],
        )
        rows = cursor.fetchall()
        assert rows[0] == (partner.slug, partner.id)

        # insert with None value
        notification_id = uuid.uuid4()
        insert_notification(cursor, user.id, notification_id, "item_parent_partner_uuid", None)
        cursor.execute(
            "SELECT item_parent_partner_id, item_parent_partner_uuid FROM notification WHERE id = %s",
            [notification_id],
        )
        rows = cursor.fetchall()
        assert rows[0] == (None, None)
        # update
        cursor.execute(
            "UPDATE notification SET item_parent_partner_uuid = %s WHERE id = %s",
            [
                partner.id,
                notification_id,
            ],
        )
        cursor.execute(
            "SELECT item_parent_partner_id, item_parent_partner_uuid FROM notification WHERE id = %s",
            [notification_id],
        )
        rows = cursor.fetchall()
        assert rows[0] == (partner.slug, partner.id)
        # update
        cursor.execute(
            "UPDATE notification SET item_parent_partner_uuid = %s WHERE id = %s",
            [
                None,
                notification_id,
            ],
        )
        cursor.execute(
            "SELECT item_parent_partner_id, item_parent_partner_uuid FROM notification WHERE id = %s",
            [notification_id],
        )
        rows = cursor.fetchall()
        assert rows[0] == (None, None)
