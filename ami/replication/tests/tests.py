import pytest


@pytest.mark.django_db
def test_get_anonymised_users(django_app) -> None:
    data = {"last_logged": "2024-11-01", "created_at": "2022-11-01", "updated_at": "2023-11-01"}

    # Appel API
    response = django_app.get("/replication/users", status=200)
    data = response.json()

    # Vérifie qu'on a pas le FC Hash et qu'on a le last_logged
    breakpoint()
    assert "fc_hash" not in data.keys()

    # Vérifier écriture dans Data Warehouse

    # assert_query_fails_without_auth(django_app, "/data/follow-up/inventories")
