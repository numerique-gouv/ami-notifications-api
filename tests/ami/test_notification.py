from litestar import Litestar
from litestar.status_codes import (
    HTTP_200_OK,
)
from litestar.testing import TestClient


async def test_notify_send_ok_with_200(
    test_client: TestClient[Litestar],
) -> None:
    notification_data = {
        "recipient_fc_hash": "4abd71ec1f581dce2ea2221cbeac7c973c6aea7bcb835acdfe7d6494f1528060",
        "item_type": "OTV",
        "item_id": "A-5-JGBJ5VMOY",
        "item_status_label": "brouillon",
        "item_generic_status": "new",
        "item_send_date": "2025-11-27T10:55:00.000Z",
        "content_title": "Brouillon de nouvelle demande de démarche d'OTV",
        "content_body": "Merci d'avoir initié votre demande",
    }
    response = test_client.post("/api/v1/notifications", json=notification_data)
    assert response.status_code == HTTP_200_OK
    assert response.json() == {
        "notification_id": "43847a2f-0b26-40a4-a452-8342a99a10a8",
        "notification_send_status": True,
    }


async def test_notify_send_ko_with_200_and_notification_send_status_to_false(
    test_client: TestClient[Litestar],
) -> None:
    notification_data = {
        "recipient_fc_hash": "unknown_hash",
        "item_type": "OTV",
        "item_id": "A-5-JGBJ5VMOY",
        "item_status_label": "brouillon",
        "item_generic_status": "new",
        "item_send_date": "2025-11-27T10:55:00.000Z",
        "content_title": "Brouillon de nouvelle demande de démarche d'OTV",
        "content_body": "Merci d'avoir initié votre demande",
    }
    response = test_client.post("/api/v1/notifications", json=notification_data)
    assert response.status_code == HTTP_200_OK
    assert response.json() == {
        "notification_id": "43847a2f-0b26-40a4-a452-8342a99a10a8",
        "notification_send_status": False,
    }
