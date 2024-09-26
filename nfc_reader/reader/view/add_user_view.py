from django.shortcuts import render, redirect
from django.views import View
from ..models import PassengerUser, Parent
from django.contrib import messages
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import JsonResponse

@login_required
def add_user_view(request):
    if request.method == 'POST':
        # Récupérer les données du formulaire
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirmPassword')
        nom = request.POST.get('nom')
        prenom = request.POST.get('prenom')
        type_utilisateur = request.POST.get('typeUtilisateur')
        sex = request.POST.get('sex')
        date_of_birth = request.POST.get('dateOfBirth')
        telephone = request.POST.get('telephone')
        address = request.POST.get('address')
        parent_name = request.POST.get('parentName')

        # Vérifier que les mots de passe correspondent
        if password != confirm_password:
            return JsonResponse({'success': False, 'message': "Les mots de passe ne correspondent pas."})

        try:
            # Créer l'utilisateur
            user = PassengerUser.objects.create(
                username=username,
                email=email,
                nom=nom,
                prenom=prenom,
                type_utilisateur=type_utilisateur,
                sex=sex,
                date_of_birth=date_of_birth,
                telephone=telephone,
                address=address,
            )
            user.set_password(password)
            user.save()

            # Si l'utilisateur est un étudiant, enregistrer le parent
            if type_utilisateur == 'etudiant' and parent_name:
                Parent.objects.create(
                    student=user,
                    nom_parent=parent_name
                )

            return JsonResponse({'success': True, 'message': "Utilisateur enregistré avec succès !"})

        except Exception as e:
            return JsonResponse({'success': False, 'message': f"Erreur lors de l'enregistrement de l'utilisateur: {e}"})
    
    return render(request, 'add_user.html')