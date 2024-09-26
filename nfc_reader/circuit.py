import os
import django

# Configuration de l'environnement Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "nfc_reader.settings")
django.setup()

# Importation du modèle Circuit après la configuration
from reader.models import Circuit

# Insertion des données pour le circuit A
Circuit.objects.create(
    name='A',
    localities="""
    Haut du cap,
    Lory,
    Bayakou,
    Nan goya,
    Kafou zoranj,
    Lagosèt,
    Pon gra,
    Laswis,
    Vedrin,
    Pon grasya,
    Dèplant,
    Nan janlwi,
    Koub Koulév
    """
)

# Insertion des données pour le circuit B
Circuit.objects.create(
    name='B',
    localities="""
    Madeline,
    Nazon,
    Bonay Dugal,
    Kafou lamò,
    Mazère,
    Kleris,
    Kafou Bonga,
    Kafou pè
    """
)

# Insertion des données pour le circuit C
Circuit.objects.create(
    name='C',
    localities="""
    Rivyé ranni,
    Bodin,
    Distrout
    """
)

print("Données insérées avec succès !")
