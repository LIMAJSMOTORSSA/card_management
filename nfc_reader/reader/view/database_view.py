from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from ..models import PassengerUser, CardInfo, SystemUser , Transaction, PassengerCard, Subscription
from datetime import date
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_http_methods
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from ..serializers import PassengerUserSerializer
from django.utils import timezone

@login_required
def card_info(request):
    cards = CardInfo.objects.all()
    today = date.today()
    return render(request, 'card_info.html', {'cards': cards, 'today': today})



@login_required
def passenger_card_database(request):
    passenger_cards = PassengerCard.objects.select_related('passenger_user', 'card_info').all()
    return render(request, 'passenger_card_database.html', {'passenger_cards': passenger_cards})



@login_required
def subscription(request):
    subscriptions = Subscription.objects.all()
    total_subscriptions = subscriptions.count()
    active_subscriptions = subscriptions.filter(is_active=True).count()
    expired_subscriptions = subscriptions.filter(is_active=False).count()
    expiring_soon = subscriptions.filter(end_date__lte=timezone.now().date() + timezone.timedelta(days=30)).count()

    context = {
        'subscriptions': subscriptions,
        'total_subscriptions': total_subscriptions,
        'active_subscriptions': active_subscriptions,
        'expired_subscriptions': expired_subscriptions,
        'expiring_soon': expiring_soon,
    }
    return render(request, 'subscription.html', context)


# Vue pour transaction_database.html
@login_required
def transaction_database(request):
    transactions = Transaction.objects.all()
    return render(request, 'transaction_database.html', {'transactions': transactions})

@login_required
@require_POST
def create_transaction(request):
    try:
        # Récupérer les données du formulaire
        passenger_user_id = request.POST.get('passenger_user_id')
        transaction_type = request.POST.get('transaction_type')
        payment_method = request.POST.get('payment_method')
        amount = request.POST.get('amount')
        details = request.POST.get('details', '')  # Par défaut, les détails peuvent être vides
        is_successful = request.POST.get('is_successful', 'true') == 'true'  # Convertir en booléen

        # Valider que le passenger_user existe
        passenger_user = PassengerUser.objects.get(id=passenger_user_id)

        # Créer la transaction
        transaction = Transaction.objects.create(
            passenger_user=passenger_user,
            transaction_type=transaction_type,
            payment_method=payment_method,
            amount=amount,
            transaction_date=timezone.now(),
            is_successful=is_successful,
            details=details
        )

        # Renvoyer une réponse JSON de succès
        return JsonResponse({'success': True, 'transaction_id': transaction.id})

    except PassengerUser.DoesNotExist:
        return JsonResponse({'success': False, 'error': "Passenger user not found."}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)

# Vue pour user_database.html
# Vue pour afficher la liste des utilisateurs
@login_required
def user_database(request):
    users = PassengerUser.objects.all()
    return render(request, 'user_database.html', {'users': users})

# API pour récupérer, mettre à jour et supprimer un utilisateur
@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def user_detail(request, pk):
    try:
        user = PassengerUser.objects.get(pk=pk)
    except PassengerUser.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = PassengerUserSerializer(user)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = PassengerUserSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
# Vue pour user_systeme.html
@login_required
def user_systeme(request):
    users = SystemUser.objects.all()
    return render(request, 'user_systeme.html', {'users': users})

@login_required
@require_POST
def add_or_update_user(request):
    user_id = request.POST.get('id')
    username = request.POST.get('username')
    email = request.POST.get('email')
    nom = request.POST.get('nom')
    prenom = request.POST.get('prenom')
    telephone = request.POST.get('telephone')
    role = request.POST.get('role')
    is_active = request.POST.get('is_active') == 'true'
    is_staff = request.POST.get('is_staff') == 'true'

    if user_id:
        # Modification de l'utilisateur existant
        user = get_object_or_404(SystemUser, id=user_id)
        user.username = username
        user.email = email
        user.nom = nom
        user.prenom = prenom
        user.telephone = telephone
        user.role = role
        user.is_active = is_active
        user.is_staff = is_staff
        user.save()
    else:
        # Ajout d'un nouvel utilisateur
        SystemUser.objects.create(
            username=username,
            email=email,
            nom=nom,
            prenom=prenom,
            telephone=telephone,
            role=role,
            is_active=is_active,
            is_staff=is_staff,
        )
    return JsonResponse({'success': True})

@login_required
@require_POST
def delete_user(request, user_id):
    user = get_object_or_404(SystemUser, id=user_id)
    user.delete()
    return JsonResponse({'success': True})