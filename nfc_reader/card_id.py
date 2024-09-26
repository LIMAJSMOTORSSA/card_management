import os
import django
from django.utils import timezone

# Configuration de l'environnement Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "nfc_reader.settings")
django.setup()

# Maintenant que Django est configuré, nous pouvons importer nos modèles
from reader.models import CardAssignmentid, UserType, Status

def populate_card_assignments():
    data = {
        UserType.PARENT: ['P000 A000 H000 T{:03d}'.format(i) for i in range(1, 101)],
        UserType.EMPLOYEE: ['E000 M000 H000 T{:03d}'.format(i) for i in range(1, 101)],
        UserType.STUDENT: ['E000 T000 H000 T{:03d}'.format(i) for i in range(1, 101)]
    }

    for user_type, codes in data.items():
        for index, code in enumerate(codes, start=1):
            # Déterminer le statut de la carte
            if (user_type in [UserType.EMPLOYEE, UserType.STUDENT] and index > 20) or (user_type == UserType.PARENT and index > 60):
                status = Status.NOT_IN_CIRCULATION
            else:
                status = Status.AVAILABLE

            # Créer l'attribution de carte avec le statut défini
            CardAssignmentid.objects.create(
                user_type=user_type,
                unique_code=code,
                status=status
            )

    print("CardAssignmentid entries have been created.")

if __name__ == "__main__": 
    populate_card_assignments()

    # Vérification
    print(f"Total entries: {CardAssignmentid.objects.count()}")
    print(f"Parents: {CardAssignmentid.objects.filter(user_type=UserType.PARENT).count()}")
    print(f"Employees: {CardAssignmentid.objects.filter(user_type=UserType.EMPLOYEE).count()}")
    print(f"Students: {CardAssignmentid.objects.filter(user_type=UserType.STUDENT).count()}")
    print(f"Not in Circulation: {CardAssignmentid.objects.filter(status=Status.NOT_IN_CIRCULATION).count()}")
    print(f"Available: {CardAssignmentid.objects.filter(status=Status.AVAILABLE).count()}")
