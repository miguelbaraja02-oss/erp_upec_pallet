import json

from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

from companies.models import CompanyUser


class InvitationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user = self.scope.get("user")
        if not user or not user.is_authenticated:
            await self.close(code=4401)
            return

        self.group_name = f"invitations_user_{user.id}"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def invitation_created(self, event):
        payload = event.get("payload", {})
        await self.send(text_data=json.dumps(payload))


class CompanyInvitationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user = self.scope.get("user")
        if not user or not user.is_authenticated:
            await self.close(code=4401)
            return

        company_id = self.scope.get("url_route", {}).get("kwargs", {}).get("company_id")
        if company_id is None:
            await self.close(code=4400)
            return

        has_access = await sync_to_async(
            CompanyUser.objects.filter(user=user, company_id=company_id, is_active=True).exists
        )()
        if not has_access:
            await self.close(code=4403)
            return

        self.group_name = f"company_invitations_{company_id}"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def invitation_status_updated(self, event):
        payload = event.get("payload", {})
        await self.send(text_data=json.dumps(payload))
