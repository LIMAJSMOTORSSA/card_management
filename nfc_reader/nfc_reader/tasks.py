# nfc_dashboard/tasks.py

import asyncio
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from reader.views import get_reader_status

async def nfc_status_loop():
    channel_layer = get_channel_layer()
    while True:
        status = {'reader_info': get_reader_status()}
        await channel_layer.group_send(
            'nfc_status_group',
            {
                'type': 'send_status',
                'status': status
            }
        )
        await asyncio.sleep(5)  # Toutes les 5 secondes

def start_nfc_status_loop():
    loop = asyncio.get_event_loop()
    loop.create_task(nfc_status_loop())
