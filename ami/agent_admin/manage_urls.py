from django.urls import path

from ami.agent_admin.views.manage import access_views, notification_views

app_name = "agent_admin"
urlpatterns = [
    path("access/", access_views.access, name="access"),
    path("notification/", notification_views.send_notification, name="send-notification"),
]
