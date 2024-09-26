# nfc_dashboard/apps.py

from django.apps import AppConfig

class NfcDashboardConfig(AppConfig):
    name = 'nfc_dashboard'

    def ready(self):
        from . import tasks
        tasks.start_nfc_status_loop()
