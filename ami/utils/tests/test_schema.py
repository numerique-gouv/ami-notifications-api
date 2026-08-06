def test_schema(app):
    resp = app.get("/schema")
    assert "/api/v1/notifications" in resp.text
    assert "/dev-utils/" not in resp.text
    assert 'spec-url="/schema"' in app.get("/schema/rapidoc")
    assert 'url: "/schema"' in app.get("/schema/swagger")

    resp = app.get("/schema/internal-apis")
    assert "/api/v1/notifications" not in resp.text
    assert "/dev-utils/" in resp.text
    assert 'spec-url="/schema/internal-apis"' in app.get("/schema/internal-apis/rapidoc")
    assert 'url: "/schema/internal\\u002Dapis"' in app.get("/schema/internal-apis/swagger")
