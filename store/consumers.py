import json

from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

from companies.models import CompanyUser
from store.models import Almacen
from store.realtime import warehouse_3d_group_name
from store.services.pallets import build_warehouse_visualization_payload


class Warehouse3DConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user = self.scope.get('user')
        if not user or not user.is_authenticated:
            await self.close(code=4401)
            return

        warehouse_id = self.scope.get('url_route', {}).get('kwargs', {}).get('warehouse_id')
        if warehouse_id is None:
            await self.close(code=4400)
            return

        warehouse = await sync_to_async(
            lambda: Almacen.objects.filter(id=warehouse_id, is_active=True).select_related('company').first()
        )()
        if not warehouse:
            await self.close(code=4404)
            return

        has_access = await sync_to_async(
            CompanyUser.objects.filter(user=user, company=warehouse.company, is_active=True).exists
        )()
        if not has_access:
            await self.close(code=4403)
            return

        self.warehouse_id = warehouse.id
        self.group_name = warehouse_3d_group_name(warehouse.id)
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        await self.send(
            text_data=json.dumps(
                {
                    'type': 'warehouse_3d_update',
                    'payload': await sync_to_async(build_warehouse_visualization_payload)(warehouse),
                }
            )
        )

    async def disconnect(self, close_code):
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def warehouse_3d_updated(self, event):
        await self.send(
            text_data=json.dumps(
                {
                    'type': 'warehouse_3d_update',
                    'payload': event.get('payload', {}),
                }
            )
        )
