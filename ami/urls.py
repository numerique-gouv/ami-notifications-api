from django.urls import path

from ami.utils import views as ami_views

urlpatterns = [
    path("ping", ami_views.ping),
]
