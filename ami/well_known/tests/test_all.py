def test_apple_app_site_association(app, settings):
    settings.IOS_APP_IDS = []
    app.get("/.well-known/apple-app-site-association", status=404)

    settings.IOS_APP_IDS = ["fake.app.id"]
    response = app.get("/.well-known/apple-app-site-association")
    assert response.json["webcredentials"]["apps"] == settings.IOS_APP_IDS


def test_assetlinks(app, settings):
    settings.ANDROID_PACKAGE_NAME = None
    app.get("/.well-known/assetlinks.json", status=404)

    settings.ANDROID_PACKAGE_NAME = "fake.app"
    settings.ANDROID_CERT_FINGERPRINTS = ["12:34"]
    response = app.get("/.well-known/assetlinks.json")
    assert response.json[0]["target"]["package_name"] == settings.ANDROID_PACKAGE_NAME
    assert (
        response.json[0]["target"]["sha256_cert_fingerprints"] == settings.ANDROID_CERT_FINGERPRINTS
    )
