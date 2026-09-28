from django.urls import include, path

from ami.well_known import views

urlpatterns = [
    path("apple-app-site-association", views.apple_app_site_association),
    path("assetlinks.json", views.assetlinks),
    path("", include("letsencrypt.urls")),
]
