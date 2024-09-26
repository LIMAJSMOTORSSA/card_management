# views.py
import os
import json
from django.views.decorators.csrf import ensure_csrf_cookie

from django.shortcuts import render
from django.core.mail import EmailMessage
from django.conf import settings
from django.http import JsonResponse
from ..forms import EmailForm

import logging
logger = logging.getLogger(__name__)

@ensure_csrf_cookie
def send_database(request):
    if request.method == 'POST':
        form = EmailForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            
            try:
                # Chemin vers la base de données
                db_path = os.path.join(settings.BASE_DIR, 'db.sqlite3')
                
                # Création de l'email
                mail = EmailMessage(
                    subject='Base de données',
                    body='Veuillez trouver ci-joint la base de données.',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[email]
                )
                
                # Ajout de la base de données comme pièce jointe
                with open(db_path, 'rb') as f:
                    mail.attach('database.sqlite3', f.read(), 'application/octet-stream')
                
                # Envoi de l'email
                mail.send()
                logger.info(f"Email envoyé avec succès à {email}")
                
                return JsonResponse({'success': True})
            except Exception as e:
                logger.error(f"Erreur lors de l'envoi de l'email: {str(e)}")
                return JsonResponse({'success': False, 'error': str(e)})
        else:
            logger.warning(f"Formulaire invalide: {form.errors}")
            return JsonResponse({'success': False, 'errors': form.errors})
    else:
        form = EmailForm()
    
    return render(request, 'send_database.html', {'form': form})