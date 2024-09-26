from django.shortcuts import render
from django.db.models import Sum
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from smartcard.System import readers
from smartcard.Exceptions import NoCardException
from ..models import PassengerUser, UnassignedCard, Transaction, TravelTransaction, CardAssignmentid, Status
from django.utils import timezone

@login_required
def home(request):
    stats = get_dashboard_stats()
    return render(request, 'home.html', {'stats': stats})

def check_nfc_reader_status(request):
    try:
        available_readers = readers()
        if available_readers:
            reader = available_readers[0]
            return JsonResponse({
                "status": "connected",
                "name": str(reader),
                "card_present": check_card_presence(reader)
            })
        else:
            return JsonResponse({"status": "disconnected", "name": "", "card_present": False})
    except Exception as e:
        return JsonResponse({"status": "error", "name": "", "card_present": False, "error": str(e)})

def check_card_presence(reader):
    try:
        connection = reader.createConnection()
        connection.connect()
        return True
    except NoCardException:
        return False
    
    
def get_dashboard_stats():
    today = timezone.now().date()
    start_of_month = today.replace(day=1)
    
    stats = {
        'total_clients': PassengerUser.objects.count(),
        'unassigned_cards': CardAssignmentid.objects.filter(status=Status.AVAILABLE).count(),
        'total_revenue': Transaction.objects.filter(
            is_successful=True,
            transaction_date__date__gte=start_of_month,
            transaction_date__date__lte=today
        ).aggregate(Sum('amount'))['amount__sum'] or 0,
        'today_transactions': TravelTransaction.objects.filter(transaction_date__date=today).count(),
    }
    
    return stats

def api_dashboard_stats(request):
    stats = get_dashboard_stats()
    return JsonResponse(stats)