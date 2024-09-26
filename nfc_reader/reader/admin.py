# admin.py

from django.contrib import admin
from django.core.exceptions import ValidationError
from .models import (
    PassengerUser,
    SystemUser,
    CardInfo,
    PassengerCard,
    Subscription,
    Transaction,
    TravelTransaction,
    CardConfiguration,
    UnassignedCard,
    CardOperation,
    CardAssignment
)

