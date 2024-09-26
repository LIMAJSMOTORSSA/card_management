from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import SystemUser
from smartcard.System import readers
from smartcard.util import toHexString
from smartcard.Exceptions import CardConnectionException, NoCardException
from .nfc_utils import read_card, write_card
from .forms import PassengerUserForm
from .models import PassengerUser, CardInfo, PassengerCard, TravelTransaction, CardInfoSim, SubscriptionSim, PassengerCardSim
from django.utils import timezone
import uuid


def assign_card(request, passenger_id):
    passenger = PassengerUser.objects.get(id=passenger_id)
    
    if request.method == 'POST':
        subscription_type = request.POST.get('subscription_type')
        payment_method = request.POST.get('payment_method')
        renewal_type = request.POST.get('renewal_type')
        auto_renew = request.POST.get('auto_renew') == 'on'

        # Générer un UID unique pour la carte
        card_uid = str(uuid.uuid4())

        # Calculer la date d'expiration
        start_date = timezone.now().date()
        if subscription_type == 'mensuel':
            end_date = start_date + timezone.timedelta(days=30)
        elif subscription_type == 'trimestriel':
            end_date = start_date + timezone.timedelta(days=90)
        elif subscription_type == 'annuel':
            end_date = start_date + timezone.timedelta(days=365)
        else:  # special
            end_date = start_date + timezone.timedelta(days=7)

        # Créer CardInfoSim
        card_info = CardInfoSim.objects.create(
            card_uid=card_uid,
            subscription_type=subscription_type,
            expiration_date=end_date,
            authentication_key=str(uuid.uuid4())  # Générer une clé d'authentification
        )

        # Créer SubscriptionSim
        subscription = SubscriptionSim.objects.create(
            passenger_user=passenger,
            subscription_type=subscription_type,
            payment_method=payment_method,
            renewal_type=renewal_type,
            auto_renew=auto_renew,
            start_date=start_date,
            end_date=end_date,
            payment_received=True
        )

        # Créer PassengerCardSim
        PassengerCardSim.objects.create(
            passenger_user=passenger,
            card_info=card_info,
            subscription=subscription
        )

        # Préparer les données à écrire sur la carte
        card_data = f"{card_uid},{subscription_type},{end_date.isoformat()}"

        # Écrire les données sur la carte
        success, message = write_card(card_data)

        if success:
            messages.success(request, f"Carte assignée avec succès. UID: {card_uid}. {message}")
            return redirect('simulation_page')
        else:
            messages.error(request, f"Erreur lors de l'écriture sur la carte: {message}")
            # Vous pouvez choisir de supprimer les objets créés en cas d'échec de l'écriture
            card_info.delete()
            subscription.delete()
            # La suppression de PassengerCardSim se fera automatiquement grâce à la suppression en cascade

    return render(request, 'assign_card.html', {
        'passenger': passenger,
        'subscription_types': SubscriptionSim.SUBSCRIPTION_CHOICES,
        'payment_methods': SubscriptionSim.PAYMENT_METHOD_CHOICES,
        'renewal_types': SubscriptionSim.RENEWAL_TYPE_CHOICES
    })
    
    
def assign_card(request, passenger_id):
    passenger = PassengerUser.objects.get(id=passenger_id)
    
    if request.method == 'POST':
        subscription_type = request.POST.get('subscription_type')
        payment_method = request.POST.get('payment_method')
        renewal_type = request.POST.get('renewal_type')
        auto_renew = request.POST.get('auto_renew') == 'on'

        # Générer un UID unique pour la carte
        card_uid = str(uuid.uuid4())

        # Calculer la date d'expiration
        start_date = timezone.now().date()
        if subscription_type == 'mensuel':
            end_date = start_date + timezone.timedelta(days=30)
        elif subscription_type == 'trimestriel':
            end_date = start_date + timezone.timedelta(days=90)
        elif subscription_type == 'annuel':
            end_date = start_date + timezone.timedelta(days=365)
        else:  # special
            end_date = start_date + timezone.timedelta(days=7)

        # Créer CardInfoSim
        card_info = CardInfoSim.objects.create(
            card_uid=card_uid,
            subscription_type=subscription_type,
            expiration_date=end_date,
            authentication_key=str(uuid.uuid4())  # Générer une clé d'authentification
        )

        # Créer SubscriptionSim
        subscription = SubscriptionSim.objects.create(
            passenger_user=passenger,
            subscription_type=subscription_type,
            payment_method=payment_method,
            renewal_type=renewal_type,
            auto_renew=auto_renew,
            start_date=start_date,
            end_date=end_date,
            payment_received=True
        )

        # Créer PassengerCardSim
        PassengerCardSim.objects.create(
            passenger_user=passenger,
            card_info=card_info,
            subscription=subscription
        )

        # Écrire les données sur la carte NFC
        card_data = {
            'uid': card_uid,
            'subscription_type': subscription_type,
            'expiration_date': end_date.isoformat()
        }
        success, message = write_card(card_data)

        if success:
            messages.success(request, f"Carte assignée avec succès. UID: {card_uid}")
            return redirect('simulation_page')
        else:
            messages.error(request, f"Erreur lors de l'écriture sur la carte: {message}")

    return render(request, 'reader/assign_card.html', {
        'passenger': passenger,
        'subscription_types': SubscriptionSim.SUBSCRIPTION_CHOICES,
        'payment_methods': SubscriptionSim.PAYMENT_METHOD_CHOICES,
        'renewal_types': SubscriptionSim.RENEWAL_TYPE_CHOICES
    })