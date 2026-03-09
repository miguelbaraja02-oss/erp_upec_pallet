from django.urls import path

from companies.consumers import CompanyInvitationConsumer, InvitationConsumer

websocket_urlpatterns = [
    path("ws/invitations/", InvitationConsumer.as_asgi(), name="ws_invitations"),
    path(
        "ws/companies/<int:company_id>/invitations/",
        CompanyInvitationConsumer.as_asgi(),
        name="ws_company_invitations",
    ),
]
