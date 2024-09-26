from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.shortcuts import render
from smartcard.System import readers
from smartcard.Exceptions import NoCardException, CardConnectionException
import time
from ..nfc_utils import get_uid, write_card, read_card

@login_required
def test_ecriture(request):
    if request.method == 'POST':
        return handle_write_request(request)
    return render(request, 'test_ecriture.html')

def detect_reader():
    available_readers = readers()
    return bool(available_readers), available_readers[0] if available_readers else "Aucun lecteur NFC détecté. Veuillez brancher un lecteur."

def wait_for_card(reader, timeout=30):
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            connection = reader.createConnection()
            connection.connect()
            uid = get_uid(connection)
            return bool(uid), uid or "Erreur lors de la lecture de l'UID de la carte."
        except (NoCardException, CardConnectionException):
            time.sleep(0.5)
    return False, "Aucune carte détectée. Veuillez placer une carte sur le lecteur."

def handle_write_request(request):
    data_to_write = request.POST.get('data', '')
    
    reader_status, reader_or_message = detect_reader()
    if not reader_status:
        return JsonResponse({'status': 'error', 'message': reader_or_message})
    
    card_status, card_uid_or_message = wait_for_card(reader_or_message)
    if not card_status:
        return JsonResponse({'status': 'error', 'message': card_uid_or_message})
    
    success, message = write_card(data_to_write)
    
    return JsonResponse({
        'status': 'success' if success else 'error',
        'message': f"Données écrites avec succès sur la carte UID: {card_uid_or_message}" if success else message
    })

# Vue pour test_lecture.html


def check_reader_and_card():
    try:
        available_readers = readers()
        if not available_readers:
            return False, "Aucun lecteur NFC détecté. Veuillez brancher un lecteur."
        
        reader = available_readers[0]
        connection = reader.createConnection()
        connection.connect()
        return True, "Lecteur et carte détectés."
    except NoCardException:
        return False, "Lecteur détecté, mais aucune carte présente. Veuillez placer une carte sur le lecteur."
    except Exception as e:
        return False, f"Erreur lors de la détection : {str(e)}"

@login_required
@require_http_methods(["GET"])
def test_lecture(request):
    reader_status, message = check_reader_and_card()
    if not reader_status:
        return render(request, 'test_lecture.html', {'error': message})
    
    card_data = read_card()
    if 'error' in card_data:
        return render(request, 'test_lecture.html', {'error': card_data['error']})
    
    return render(request, 'test_lecture.html', {'card_data': card_data, 'success': "Carte lue avec succès."})
# Vue pour test_transaction.html
@login_required
def test_transaction(request):
    return render(request, 'test_transaction.html') 