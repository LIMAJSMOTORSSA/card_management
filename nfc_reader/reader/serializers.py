from rest_framework import serializers
from .models import PassengerUser

class PassengerUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = PassengerUser
        fields = [
            'id', 'username', 'email', 'nom', 'prenom', 'type_utilisateur',
            'account_status', 'sex', 'date_of_birth', 'address', 'telephone',
        ]
