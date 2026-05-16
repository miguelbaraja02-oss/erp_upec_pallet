from django.urls import path

from companies.consumers import CompanyInvitationConsumer, InvitationConsumer
from store.consumers import Warehouse3DConsumer

websocket_urlpatterns = [
    path("ws/invitations/", InvitationConsumer.as_asgi(), name="ws_invitations"),
    path(
        "ws/companies/<int:company_id>/invitations/",
        CompanyInvitationConsumer.as_asgi(),
        name="ws_company_invitations",
    ),
    path(
        "ws/store/warehouses/<int:warehouse_id>/3d/",
        Warehouse3DConsumer.as_asgi(),
        name="ws_warehouse_3d",
    ),
]
