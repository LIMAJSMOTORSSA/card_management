from django.shortcuts import render, get_object_or_404 , redirect
from django.http import JsonResponse
from django.db.models import Q
from ..models import PassengerUser, CardAssignmentid, CardInfo, PassengerCard
from django.utils import timezone
import random
import string


def search_usernfc(request):
    query = request.GET.get('query', '')
    users = PassengerUser.objects.filter(
        Q(nom__icontains=query) | 
        Q(prenom__icontains=query) | 
        Q(passengerid__icontains=query)
    )[:10]  # Limiter à 10 résultats pour la performance
    
    results = [{'id': user.id, 'name': f"{user.nom} {user.prenom}", 'passengerid': user.passengerid} for user in users]
    return JsonResponse(results, safe=False)

def user_search_page(request):
    return render(request, 'nfcattribution/user_search.html')




def get_card_assignments(request):
    user_id = request.GET.get('user_id')
    user = get_object_or_404(PassengerUser, id=user_id)
    
    user_type_map = {
        'parent': 'P',
        'employee': 'E',
        'student': 'S',
    }
    user_type = user_type_map.get(user.type_utilisateur, '')
    
    assignments = CardAssignmentid.objects.filter(
        user_type=user_type,
        status='available'
    )
    
    results = [{'id': a.id, 'unique_code': a.unique_code} for a in assignments]
    return JsonResponse(results, safe=False)

def card_assignment_page(request, user_id):
    user = get_object_or_404(PassengerUser, id=user_id)
    return render(request, 'nfcattribution/card_assignment.html', {'user': user})


def create_card(request):
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        assignment_id = request.POST.get('assignment_id')
        
        user = get_object_or_404(PassengerUser, id=user_id)
        assignment = get_object_or_404(CardAssignmentid, id=assignment_id)
        
        # Vérifier que la carte est toujours disponible
        if assignment.status != 'available':
            return render(request, 'nfcattribution/card_creation_error.html', {'error': 'Cette carte n\'est plus disponible.'})
        
        # Générer des données aléatoires pour la carte
        card_uid = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
        authentication_key = ''.join(random.choices(string.ascii_uppercase + string.digits, k=16))
        secret_code = ''.join(random.choices(string.digits, k=6))
        
        # Créer l'entrée CardInfo
        # Créer l'entrée CardInfo
        card_info = CardInfo.objects.create(
            card_uid=card_uid,
            expiration_date=timezone.now() + timezone.timedelta(days=365),
            card_assignment=assignment
        )

        # Définir les clés chiffrées
        card_info.set_authentication_key(authentication_key)
        card_info.set_secret_code(secret_code)
        card_info.save()
        # Créer l'entrée PassengerCard
        PassengerCard.objects.create(passenger_user=user, card_info=card_info)
        
        # Écrire les données sur la carte NFC
        from ..nfcreadingutils import write_card_sector_12
        success, message = write_card_sector_12(card_info)
        
        if success:
            # Changer le statut de l'assignment à 'ASSIGNED'
            assignment.status = 'assigned'
            assignment.save()
            return render(request, 'nfcattribution/card_creation_success.html', {'card_info': card_info})
        else:
            # En cas d'échec, supprimer les entrées créées
            PassengerCard.objects.filter(card_info=card_info).delete()
            card_info.delete()
            return render(request, 'nfcattribution/card_creation_error.html', {'error': message})
    
    return redirect(request, 'nfcattribution/create_card.html')