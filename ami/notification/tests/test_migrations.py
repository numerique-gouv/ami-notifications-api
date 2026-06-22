import uuid

import pytest
from django.db import connection
from django.utils.timezone import now


@pytest.mark.django_db
def test_send_date_migration(app, user):
    def insert_notification(cursor, user_id, notification_id, field, value):
        cursor.execute(
            f"""
    INSERT INTO notification (
      id,
      user_id,
      content_body,
      content_title,
      partner_id,
      read,
      created_at,
      updated_at,
      {field}
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            [
                notification_id,
                user_id,
                "",
                "",
                "",
                False,
                now(),
                now(),
                value,
            ],
        )

    # test with old code
    with connection.cursor() as cursor:
        # insert
        notification_id = uuid.uuid4()
        send_date = now()
        insert_notification(cursor, user.id, notification_id, "send_date", send_date)
        cursor.execute(
            "SELECT send_date, event_date FROM notification WHERE id = %s", [notification_id]
        )
        rows = cursor.fetchall()
        assert rows[0] == (send_date, send_date)

        # update
        send_date = now()
        cursor.execute(
            "UPDATE notification SET send_date = %s WHERE id = %s",
            [
                send_date,
                notification_id,
            ],
        )
        cursor.execute(
            "SELECT send_date, event_date FROM notification WHERE id = %s", [notification_id]
        )
        rows = cursor.fetchall()
        assert rows[0] == (send_date, send_date)

    # test with new code
    with connection.cursor() as cursor:
        # insert
        notification_id = uuid.uuid4()
        event_date = now()
        insert_notification(cursor, user.id, notification_id, "event_date", event_date)
        cursor.execute(
            "SELECT send_date, event_date FROM notification WHERE id = %s", [notification_id]
        )
        rows = cursor.fetchall()
        assert rows[0] == (event_date, event_date)

        # update
        event_date = now()
        cursor.execute(
            "UPDATE notification SET event_date = %s WHERE id = %s",
            [
                event_date,
                notification_id,
            ],
        )
        cursor.execute(
            "SELECT send_date, event_date FROM notification WHERE id = %s", [notification_id]
        )
        rows = cursor.fetchall()
        assert rows[0] == (event_date, event_date)


@pytest.mark.django_db
def test_item_external_url_migration(app, user):
    def insert_notification(cursor, user_id, notification_id, field, value):
        cursor.execute(
            f"""
    INSERT INTO notification (
      id,
      user_id,
      content_body,
      content_title,
      partner_id,
      read,
      event_date,
      created_at,
      updated_at,
      {field}
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            [
                notification_id,
                user_id,
                "",
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
        item_external_url = "link1"
        insert_notification(
            cursor, user.id, notification_id, "item_external_url", item_external_url
        )
        cursor.execute(
            "SELECT item_external_url, content_link FROM notification WHERE id = %s",
            [notification_id],
        )
        rows = cursor.fetchall()
        assert rows[0] == (item_external_url, item_external_url)

        # update
        item_external_url = "link2"
        cursor.execute(
            "UPDATE notification SET item_external_url = %s WHERE id = %s",
            [
                item_external_url,
                notification_id,
            ],
        )
        cursor.execute(
            "SELECT item_external_url, content_link FROM notification WHERE id = %s",
            [notification_id],
        )
        rows = cursor.fetchall()
        assert rows[0] == (item_external_url, item_external_url)

    # test with new code
    with connection.cursor() as cursor:
        # insert
        notification_id = uuid.uuid4()
        content_link = "link3"
        insert_notification(cursor, user.id, notification_id, "content_link", content_link)
        cursor.execute(
            "SELECT item_external_url, content_link FROM notification WHERE id = %s",
            [notification_id],
        )
        rows = cursor.fetchall()
        assert rows[0] == (content_link, content_link)

        # update
        content_link = "link4"
        cursor.execute(
            "UPDATE notification SET content_link = %s WHERE id = %s",
            [
                content_link,
                notification_id,
            ],
        )
        cursor.execute(
            "SELECT item_external_url, content_link FROM notification WHERE id = %s",
            [notification_id],
        )
        rows = cursor.fetchall()
        assert rows[0] == (content_link, content_link)
