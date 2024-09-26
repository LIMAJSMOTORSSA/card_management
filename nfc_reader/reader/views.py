# nfc_dashboard/views.py
#dont forget login required
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
from .models import PassengerUser, CardInfo, PassengerCard, TravelTransaction, CardInfoSim, SubscriptionSim, PassengerCardSim, TravelTransactionSim
from django.utils import timezone
from django.views.decorators.http import require_http_methods
import uuid
import json
from django.views.decorators.csrf import csrf_exempt



def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')  # Assurez-vous d'avoir une vue 'dashboard'
        else:
            messages.error(request, "Nom d'utilisateur ou mot de passe incorrect.")
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

def home(request):
    reader_info = get_reader_status()
    context = {
        'reader_info': reader_info
    }
    return render(request, 'home.html', context)

def home_ajax(request):
    reader_info = get_reader_status()
    return JsonResponse({'reader_info': reader_info})

def get_reader_status():
    reader_info = []
    try:
        reader_list = readers()
        if not reader_list:
            # Aucun lecteur détecté
            reader_info.append({
                'name': 'Aucun Lecteur',
                'type': 'N/A',
                'connected': False,
                'card_present': False,
                'error': 'Aucun lecteur détecté.'
            })
        else:
            for reader in reader_list:
                reader_details = {}
                reader_details['name'] = reader.name
                reader_details['connected'] = True
                try:
                    connection = reader.createConnection()
                    connection.connect()
                    # Détecter le type de lecteur si possible
                    if "ACR122U" in reader.name.upper():
                        reader_details['type'] = "ACS ACR122U PICC"
                    else:
                        reader_details['type'] = reader.name
                    reader_details['card_present'] = True
                except NoCardException:
                    # Aucun carte présente dans le lecteur
                    if "ACR122U" in reader.name.upper():
                        reader_details['type'] = "ACS ACR122U PICC"
                    else:
                        reader_details['type'] = reader.name
                    reader_details['card_present'] = False
                except Exception as e:
                    # Autres exceptions
                    if "ACR122U" in reader.name.upper():
                        reader_details['type'] = "ACS ACR122U PICC"
                    else:
                        reader_details['type'] = reader.name
                    reader_details['card_present'] = False
                    reader_details['error'] = str(e)
                finally:
                    try:
                        connection.disconnect()
                    except:
                        pass
                reader_info.append(reader_details)
    except Exception as e:
        print(f"Erreur lors de la détection des lecteurs : {str(e)}")
        reader_info.append({
            'name': 'Erreur',
            'type': 'N/A',
            'connected': False,
            'card_present': False,
            'error': str(e)
        })
    return reader_info



@csrf_exempt  # Note: Dans un environnement de production, gérez le CSRF correctement
def nfc_interface(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        action = data.get('action')
        if action == 'read':
            card_data = read_card()
            return JsonResponse(card_data)
        elif action == 'write':
            write_data = data.get('data')
            if not write_data:
                return JsonResponse({'success': False, 'message': 'Aucune donnée à écrire fournie.'})
            success, message = write_card(write_data)
            return JsonResponse({'success': success, 'message': message})
    return render(request, 'nfc_interface.html')

def write_nfc_card(request):
    if request.method == 'POST':
        data = request.POST.get('data', '')
        success = write_card(data)
        return render(request, 'write_result.html', {'success': success})
    return render(request, 'write_card.html')



def simulation_dashboard(request):
    return render(request, 'nfc_simulation/dashboard.html')


def create_passenger(request):
    if request.method == 'POST':
        form = PassengerUserForm(request.POST)
        if form.is_valid():
            passenger = form.save()
            return redirect('assign_card', passenger_id=passenger.id)
    else:
        form = PassengerUserForm()
    return render(request, 'nfc_simulation/create_passenger.html', {'form': form})


def assign_card(request, passenger_id):
    passenger = PassengerUser.objects.get(id=passenger_id)
    if request.method == 'POST':
        card_uid = request.POST.get('card_uid')
        subscription_type = request.POST.get('subscription_type')
        expiration_date = request.POST.get('expiration_date')
        
        card_info = CardInfoSim.objects.create(
            card_uid=card_uid,
            subscription_type=subscription_type,
            expiration_date=expiration_date
        )
        
        subscription = SubscriptionSim.objects.create(
            passenger_user=passenger,
            subscription_type=subscription_type,
            start_date=timezone.now().date(),
            end_date=expiration_date
        )
        
        PassengerCardSim.objects.create(
            passenger_user=passenger,
            card_info=card_info,
            subscription=subscription
        )
        
        # Write data to NFC card
        data = f"{card_uid},{subscription_type},{expiration_date}"
        success, message = write_card(data)
        if success:
            return redirect('simulation_dashboard')
        else:
            return render(request, 'nfc_simulation/assign_card.html', {'passenger': passenger, 'error': message})
    
    return render(request, 'nfc_simulation/assign_card.html', {'passenger': passenger})


def read_nfc_card(request):
    card_data = read_card()
    if 'error' in card_data:
        return JsonResponse({'error': card_data['error']})
    
    try:
        sector_data = card_data['sectors'][3][12]['ascii']  # Assuming data is in sector 3, block 12
        card_uid, subscription_type, expiration_date = sector_data.split(',')
        
        passenger_card = PassengerCardSim.objects.get(card_info__card_uid=card_uid)
        passenger = passenger_card.passenger_user
        
        current_date = timezone.now().date()
        is_valid = current_date <= passenger_card.subscription.end_date
        
        return JsonResponse({
            'passenger_name': f"{passenger.nom} {passenger.prenom}",
            'card_uid': card_uid,
            'subscription_type': subscription_type,
            'expiration_date': expiration_date,
            'is_valid': is_valid
        })
    except Exception as e:
        return JsonResponse({'error': str(e)})


def process_boarding(request):
    if request.method == 'POST':
        card_uid = request.POST.get('card_uid')
        is_approved = request.POST.get('is_approved') == 'true'
        
        passenger_card = PassengerCardSim.objects.get(card_info__card_uid=card_uid)
        
        TravelTransactionSim.objects.create(
            passenger_card=passenger_card,
            is_approved=is_approved,
            reason="Simulation" if is_approved else "Abonnement expiré",
            location="Simulation Station",
            processed_by=request.user
        )
        
        return JsonResponse({'success': True})
    
    return JsonResponse({'error': 'Invalid request method'})