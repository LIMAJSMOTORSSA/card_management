import os
import django

# Configuration de l'environnement Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "nfc_reader.settings")
django.setup()

# Maintenant que Django est configuré, nous pouvons importer nos modèles
from reader.models import SubscriptionPlan  # Assure-toi que le modèle SubscriptionPlan est bien dans reader.models

# Données pour les étudiants des circuits A et B
data_students_circuit_AB = [
    # Circuit A
    {
        "user_type": "employee",
        "circuit": "A",
        "locality": "Haut du cap",
        "duration": "monthly",
        "price": 6000.00,
        "registration_fee": 1000.00,
    },
    {
        "user_type": "employee",
        "circuit": "A",
        "locality": "Lory",
        "duration": "monthly",
        "price": 4000.00,
        "registration_fee": 1000.00,
    },
    {
        "user_type": "employee",
        "circuit": "A",
        "locality": "Bayakou",
        "duration": "monthly",
        "price": 4000.00,
        "registration_fee": 1000.00,
    },
    {
        "user_type": "employee",
        "circuit": "A",
        "locality": "Nan goya",
        "duration": "monthly",
        "price": 4000.00,
        "registration_fee": 1000.00,
    },
    {
        "user_type": "employee",
        "circuit": "A",
        "locality": "Kafou zoranj",
        "duration": "monthly",
        "price": 2000.00,
        "registration_fee": 1000.00,
    },
    {
        "user_type": "employee",
        "circuit": "A",
        "locality": "Lagosèt",
        "duration": "monthly",
        "price": 4000.00,
        "registration_fee": 1000.00,
    },
    {
        "user_type": "employee",
        "circuit": "A",
        "locality": "Pon gra",
        "duration": "monthly",
        "price": 4000.00,
        "registration_fee": 1000.00,
    },
    {
        "user_type": "employee",
        "circuit": "A",
        "locality": "Laswis",
        "duration": "monthly",
        "price": 4000.00,
        "registration_fee": 1000.00,
    },
    {
        "user_type": "employee",
        "circuit": "A",
        "locality": "Vedrin",
        "duration": "monthly",
        "price": 4000.00,
        "registration_fee": 1000.00,
    },
    {
        "user_type": "employee",
        "circuit": "A",
        "locality": "Pon grasya",
        "duration": "monthly",
        "price": 4000.00,
        "registration_fee": 1000.00,
    },
    {
        "user_type": "employee",
        "circuit": "A",
        "locality": "Dèplant",
        "duration": "monthly",
        "price": 4000.00,
        "registration_fee": 1000.00,
    },
    {
        "user_type": "employee",
        "circuit": "A",
        "locality": "Nan janlwi",
        "duration": "monthly",
        "price": 4000.00,
        "registration_fee": 1000.00,
    },
    {
        "user_type": "employee",
        "circuit": "A",
        "locality": "Koub Koulév",
        "duration": "monthly",
        "price": 4000.00,
        "registration_fee": 1000.00,
    },
    # Circuit B
    {
        "user_type": "employee",
        "circuit": "B",
        "locality": "Madeline",
        "duration": "monthly",
        "price": 7000.00,
        "registration_fee": 1000.00,
    },
    {
        "user_type": "employee",
        "circuit": "B",
        "locality": "Nazon",
        "duration": "monthly",
        "price": 6000.00,
        "registration_fee": 1000.00,
    },
    {
        "user_type": "employee",
        "circuit": "B",
        "locality": "Bonay Dugal",
        "duration": "monthly",
        "price": 5000.00,
        "registration_fee": 1000.00,
    },
    {
        "user_type": "employee",
        "circuit": "B",
        "locality": "Kafou lamò",
        "duration": "monthly",
        "price": 5000.00,
        "registration_fee": 1000.00,
    },
    {
        "user_type": "employee",
        "circuit": "B",
        "locality": "Mazère",
        "duration": "monthly",
        "price": 4000.00,
        "registration_fee": 1000.00,
    },
    {
        "user_type": "employee",
        "circuit": "B",
        "locality": "Kleris",
        "duration": "monthly",
        "price": 4000.00,
        "registration_fee": 1000.00,
    },
    {
        "user_type": "employee",
        "circuit": "B",
        "locality": "Kafou Bonga",
        "duration": "monthly",
        "price": 4000.00,
        "registration_fee": 1000.00,
    },
    {
        "user_type": "employee",
        "circuit": "B",
        "locality": "Kafou pè",
        "duration": "monthly",
        "price": 2000.00,
        "registration_fee": 1000.00,
    },
    # Circuit C
    {
        "user_type": "employee",
        "circuit": "C",
        "locality": "Rivyé ranni",
        "duration": "monthly",
        "price": 3500.00,
        "registration_fee": 1000.00,
    },
    {
        "user_type": "employee",
        "circuit": "C",
        "locality": "Bodin",
        "duration": "monthly",
        "price": 3500.00,
        "registration_fee": 1000.00,
    },
    {
        "user_type": "employee",
        "circuit": "C",
        "locality": "Distrout",
        "duration": "monthly",
        "price": 3500.00,
        "registration_fee": 1000.00,
    },
]

# Insérer les données dans la base de données
for item in data_students_circuit_AB:
    subscription_plan, created = SubscriptionPlan.objects.get_or_create(
        user_type=item["user_type"],
        circuit=item["circuit"],
        locality=item["locality"],
        duration=item["duration"],
        defaults={
            "price": item["price"],
            "registration_fee": item["registration_fee"]
        }
    )
    if created:
        print(f"Created subscription plan: {subscription_plan}")
    else:
        print(f"Subscription plan already exists: {subscription_plan}")
