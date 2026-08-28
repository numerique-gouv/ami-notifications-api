from django.urls import path

from ami.agent_admin.views.manage import (
    access_views,
    notification_views,
    partner_views,
    service_views,
    user_views,
)

app_name = "agent_admin"
urlpatterns = [
    path("access/", access_views.access, name="access"),
    path("notification/", notification_views.send_notification, name="send-notification"),
    path("user/", user_views.search_user, name="search-user"),
    path("user/<uuid:user_id>/", user_views.detail_user, name="detail-user"),
    path("user/<uuid:user_id>/delete/", user_views.delete_user, name="delete-user"),
    path("service/", service_views.list_services, name="list-services"),
    path("service/add/<str:kind>/", service_views.add_service, name="add-service"),
    path("service/<uuid:service_id>/", service_views.edit_service, name="edit-service"),
    path("service/<uuid:service_id>/delete/", service_views.delete_service, name="delete-service"),
    path("partner/", partner_views.list_partners, name="list-partners"),
    path("partner/add/", partner_views.add_partner, name="add-partner"),
    path("partner/<uuid:partner_id>/", partner_views.edit_partner, name="edit-partner"),
]
