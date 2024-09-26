# nfc_dashboard/routing.py

from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/nfc_status/$', consumers.NFCStatusConsumer.as_asgi()),
]
