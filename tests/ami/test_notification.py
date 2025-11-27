from litestar import Litestar
from litestar.status_codes import (
    HTTP_200_OK,
    HTTP_400_BAD_REQUEST,
    HTTP_500_INTERNAL_SERVER_ERROR,
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


async def test_notify_send_ko_with_400_when_required_fields_are_missing(
    test_client: TestClient[Litestar],
) -> None:
    notification_data: dict[str, str] = {}
    response = test_client.post("/api/v1/notifications", json=notification_data)
    assert response.status_code == HTTP_400_BAD_REQUEST
    assert response.json() == {
        "detail": "Validation failed for POST /api/v1/notifications",
        "extra": [
            {
                "key": "recipient_fc_hash",
                "message": "Field required",
            },
            {
                "key": "item_type",
                "message": "Field required",
            },
            {
                "key": "item_id",
                "message": "Field required",
            },
            {
                "key": "item_status_label",
                "message": "Field required",
            },
            {
                "key": "item_generic_status",
                "message": "Field required",
            },
            {
                "key": "item_send_date",
                "message": "Field required",
            },
            {
                "key": "content_title",
                "message": "Field required",
            },
            {
                "key": "content_body",
                "message": "Field required",
            },
        ],
        "status_code": 400,
    }


async def test_notify_send_ko_with_400_when_required_fields_are_empty(
    test_client: TestClient[Litestar],
) -> None:
    notification_data = {
        "recipient_fc_hash": "",
        "item_type": "",
        "item_id": "",
        "item_status_label": "",
        "item_generic_status": "",
        "item_send_date": "",
        "content_title": "",
        "content_body": "",
    }
    response = test_client.post("/api/v1/notifications", json=notification_data)
    assert response.status_code == HTTP_400_BAD_REQUEST
    assert response.json() == {
        "detail": "Validation failed for POST /api/v1/notifications",
        "extra": [
            {
                "key": "item_generic_status",
                "message": "Input should be 'new', 'wip' or 'closed'",
            },
            {
                "key": "item_send_date",
                "message": "Input should be a valid datetime or date, input is too short",
            },
        ],
        "status_code": 400,
    }


async def test_notify_send_ko_with_500_when_technical_error(
    test_client: TestClient[Litestar],
) -> None:
    notification_data = {
        "recipient_fc_hash": "technical_error",
        "item_type": "OTV",
        "item_id": "A-5-JGBJ5VMOY",
        "item_status_label": "brouillon",
        "item_generic_status": "new",
        "item_send_date": "2025-11-27T10:55:00.000Z",
        "content_title": "Brouillon de nouvelle demande de démarche d'OTV",
        "content_body": "Merci d'avoir initié votre demande",
    }
    response = test_client.post("/api/v1/notifications", json=notification_data)
    assert response.status_code == HTTP_500_INTERNAL_SERVER_ERROR
