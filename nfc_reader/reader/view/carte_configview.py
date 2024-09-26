import json
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required

from ..securityutils import update_nfc_security_key

@login_required
def add_card(request):
    return render(request, 'add_card.html')

@login_required
def card_list(request):
    return render(request, 'card_list.html')

@login_required
@require_http_methods(["GET", "POST"])
def change_security_key(request):
    if request.method == 'GET':
        return render(request, 'change_security_key.html')
    else:
        try:
            data = json.loads(request.body)
            form = SecurityKeyForm(data)
            if form.is_valid():
                new_key_hex = form.cleaned_data['new_key']
                new_key_bytes = bytes.fromhex(new_key_hex)
                # Appeler la fonction pour mettre à jour la clé NFC
                result = update_nfc_security_key(new_key_bytes)
                if result['status'] == 'success':
                    return JsonResponse({'status': 'success'})
                else:
                    return JsonResponse({'status': 'error', 'message': result['message']})
            else:
                errors = form.errors.get_json_data()
                return JsonResponse({'status': 'error', 'errors': errors})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
        
        
        
        
@login_required
def format_card(request):
    return render(request, 'format_card.html')