from django.urls import path

from ami.replication import api_views

app_name = "replication"
urlpatterns = [
    path("users/", api_views.get_anonymised_users),
]
