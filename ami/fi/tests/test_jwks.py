def test_jwks(
    app,
    settings,
) -> None:
    settings.FI_PUBLIC_KEY_PEM = """-----BEGIN PUBLIC KEY-----
MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAEiE6BySwCPar5xw4ftKWA53oRScxM
dYTur2ZBpo87ixjtKgixY0IZPPBysY8ji0hqLexMzyPn0awzUcUpzAuV3Q==
-----END PUBLIC KEY-----"""
    settings.FI_PRIVATE_KEY_PEM = """-----BEGIN EC PRIVATE KEY-----
MHcCAQEEIDhlh6aexVQQGXn4ZneIQQ3SjuLyAMD9lUJC96Xdwu/+oAoGCCqGSM49
AwEHoUQDQgAEiE6BySwCPar5xw4ftKWA53oRScxMdYTur2ZBpo87ixjtKgixY0IZ
PPBysY8ji0hqLexMzyPn0awzUcUpzAuV3Q==
-----END EC PRIVATE KEY-----"""
    response = app.get("/api/v1/fi/jwks/")
    assert response.json["keys"][0]["alg"] == "ES256"
