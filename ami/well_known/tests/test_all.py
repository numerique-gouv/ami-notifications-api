def test_apple_app_site_association(app, settings):
    settings.IOS_APP_IDS = []
    app.get("/.well-known/apple-app-site-association", status=404)

    settings.IOS_APP_IDS = ["fake.app.id"]
    response = app.get("/.well-known/apple-app-site-association")
    assert response.json["webcredentials"]["apps"] == settings.IOS_APP_IDS
