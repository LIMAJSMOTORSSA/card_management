# nfc_dashboard/consumers.py

import json
from channels.generic.websocket import AsyncWebsocketConsumer
import asyncio

class NFCStatusConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add(
            'nfc_status_group',
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            'nfc_status_group',
            self.channel_name
        )

    # Receive message from group
    async def send_status(self, event):
        status = event['status']
        await self.send(text_data=json.dumps(status))
