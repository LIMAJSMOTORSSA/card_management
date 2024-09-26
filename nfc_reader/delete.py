import os
import django
from django.utils import timezone

# Configuration de l'environnement Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "nfc_reader.settings")
django.setup()

# Importer le modèle que tu veux manipuler
from reader.models import CardAssignmentid  # Remplace 'yourapp' par le nom de ton application

# Fonction pour supprimer tous les enregistrements de PassengerCard
def clear_passenger_cards():
    CardAssignmentid.objects.all().delete()
    print(f"Tous les enregistrements de PassengerCard ont été supprimés à {timezone.now()}.")

# Appel de la fonction pour supprimer les enregistrements
if __name__ == "__main__":
    clear_passenger_cards()
