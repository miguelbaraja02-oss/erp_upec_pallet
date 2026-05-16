from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from store.models import Almacen
from store.services.pallets import build_warehouse_visualization_payload


def warehouse_3d_group_name(warehouse_id: int) -> str:
    return f"warehouse_3d_{warehouse_id}"


def broadcast_warehouse_3d_update(warehouse_id: int) -> None:
    channel_layer = get_channel_layer()
    if channel_layer is None:
        return

    warehouse = Almacen.objects.filter(id=warehouse_id, is_active=True).select_related('company').first()
    if not warehouse:
        return

    async_to_sync(channel_layer.group_send)(
        warehouse_3d_group_name(warehouse.id),
        {
            'type': 'warehouse_3d_updated',
            'payload': build_warehouse_visualization_payload(warehouse),
        },
    )
