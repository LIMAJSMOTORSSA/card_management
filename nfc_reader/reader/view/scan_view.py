from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from ..models import CardInfo, PassengerCard, Subscription, TravelTransaction, PassengerUser
from ..sanfrcutils import read_sector_12
from django.http import JsonResponse



@login_required
def nfc(request):
    return render(request, 'nfc.html')


@login_required
@csrf_exempt
def process_nfc_scan(request):
    card_uid = read_sector_12()
    
    if not card_uid:
        return JsonResponse({'success': False, 'error': 'Échec de lecture de la carte'})
    
    try:
        # 1. Recherche de la carte dans CardInfo
        card_info = CardInfo.objects.filter(card_uid=card_uid).first()
        if not card_info:
            return JsonResponse({'success': False, 'error': 'Carte non reconnue'})
        
        # 2. Vérification de l'expiration de la carte
        if card_info.expiration_date < timezone.now().date():
            return JsonResponse({'success': False, 'error': 'Carte expirée'})
        
        # 3. Trouver le propriétaire de la carte
        passenger_card = PassengerCard.objects.get(card_info=card_info)
        passenger = passenger_card.passenger_user
        
        # 4. Vérifier les abonnements de l'utilisateur
        active_subscriptions = Subscription.objects.filter(
            passenger_user=passenger,
            is_active=True,
            end_date__gte=timezone.now().date()
        )
        
        if not active_subscriptions:
            return JsonResponse({'success': False, 'error': 'Aucun abonnement actif'})
        
        # 5. Récupérer les informations des abonnements et des localités
        subscription_info = []
        for subscription in active_subscriptions:
            plan = subscription.plan
            subscription_info.append({
                'type': plan.get_user_type_display(),
                'locality': plan.locality,
                'circuit': plan.circuit,
                'duration': plan.get_duration_display(),
                'expiration_date': subscription.end_date.strftime('%Y-%m-%d')
            })
        
        # 6. Préparer les données à renvoyer
        response_data = {
            'success': True,
            'passenger_id': passenger.passengerid,
            'full_name': f"{passenger.nom} {passenger.prenom}",
            'name': passenger.nom,
            'surname': passenger.prenom,
            'user_type': passenger.get_type_utilisateur_display(),
            'account_status': passenger.get_account_status_display(),
            'subscriptions': subscription_info,
            'card_uid': card_info.card_uid
        }
        
        return JsonResponse(response_data)
    
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})
    
    

@login_required
@csrf_exempt
def approve_boarding(request):
    if request.method == 'POST':
        card_uid = request.POST.get('card_uid')
        is_approved = request.POST.get('is_approved') == 'true'
        location = request.POST.get('location')

        try:
            card_info = CardInfo.objects.get(card_uid=card_uid)
            passenger_card = PassengerCard.objects.get(card_info=card_info)
            passenger = passenger_card.passenger_user

            # Créer une nouvelle entrée dans TravelTransaction
            TravelTransaction.objects.create(
                passenger_user=passenger,
                card_info=card_info,
                is_approved=is_approved,
                reason='' if is_approved else 'Not specified',
                location=location,
                processed_by=request.user  # Assurez-vous que l'authentification utilisateur est en place
            )

            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@login_required
def qr_code(request):
    return render(request, 'qr_code.html')