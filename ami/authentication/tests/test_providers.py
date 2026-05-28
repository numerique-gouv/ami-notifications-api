def test_providers(settings, app) -> None:
    settings.API_PARTICULIER_QUOTIENT_ENABLED = False
    settings.API_PARTICULIER_STATUT_ETUDIANT_ENABLED = False

    response = app.get("/api/v1/authentication/providers/")
    assert response.json == {}

    settings.API_PARTICULIER_QUOTIENT_ENABLED = True
    settings.API_PARTICULIER_STATUT_ETUDIANT_ENABLED = True

    response = app.get("/api/v1/authentication/providers/")
    assert response.json == {
        "api_particulier_quotient": "API Particulier - Quotient familial CAF & MSA",
        "api_particulier_statut_etudiant": "API Particulier - Statut étudiant",
    }
