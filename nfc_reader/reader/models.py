from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.hashers import make_password, check_password
from django.conf import settings
from cryptography.fernet import Fernet
from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils.translation import gettext_lazy as _
import uuid
import random
import string

class SubscriptionPlan(models.Model):
    USER_TYPE_CHOICES = [
        ('parent', 'Parent'),
        ('employee', 'Employé'),
        ('student', 'Étudiant'),
        ('special', 'Spécial'),
    ]
    DURATION_CHOICES = [
        ('monthly', 'Mensuel'),
        ('quarterly', 'Trimestriel'),
    ]
    
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES)
    circuit = models.CharField(max_length=50)  # A, B, ou C
    locality = models.CharField(max_length=100)
    duration = models.CharField(max_length=20, choices=DURATION_CHOICES)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    registration_fee = models.DecimalField(max_digits=10, decimal_places=2, default=1000.00)

    class Meta:
        unique_together = ('user_type', 'circuit', 'locality', 'duration')

    def __str__(self):
        return f"{self.get_user_type_display()} - Circuit {self.circuit} - {self.locality} - {self.get_duration_display()}"

class UserType(models.TextChoices):
    PARENT = 'P', 'Parent'
    EMPLOYEE = 'E', 'Employee'
    STUDENT = 'S', 'Student'

class Status(models.TextChoices):
    NOT_IN_CIRCULATION = 'not_in_circulation', 'Not in Circulation'
    ASSIGNED = 'assigned', 'Assigned'
    AVAILABLE = 'available', 'Available'

class CardAssignmentid(models.Model):
    user_type = models.CharField(
        max_length=1,
        choices=UserType.choices,
        default=UserType.STUDENT,
        help_text="The type of user: Parent, Employee, or Student."
    )
    unique_code = models.CharField(
        max_length=20,
        unique=True,
        help_text="The unique card assignment number for each user."
    )
    status = models.CharField(
        max_length=20,  # Adjusted length for new status values
        choices=Status.choices,
        default=Status.NOT_IN_CIRCULATION,
        help_text="The card status (Not in Circulation, Assigned, or Available)."
    )
    assigned_on = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.unique_code:
            self.unique_code = self.generate_unique_code()
        super().save(*args, **kwargs)

    def generate_unique_code(self):
        # Your logic to generate a unique code
        pass

    def __str__(self):
        return f"{self.unique_code} ({self.get_user_type_display()})"















class SystemUserManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        if not email:
            raise ValueError(_('The Email field must be set'))
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(username, email, password, **extra_fields)

class PassengerUser(models.Model):
    USER_TYPE_CHOICES = [
        ('parent', 'Parent'),
        ('etudiant', 'Étudiant'),
        ('employee', 'Employé'),
        ('special', 'Spécial'),
    ]

    ACCOUNT_STATUS_CHOICES = [
        ('active', 'Actif'),
        ('inactive', 'Inactif'),
        ('suspended', 'Suspendu'),
        ('pending', 'En attente'),
    ]

    SEX_CHOICES = [
        ('male', 'Homme'),
        ('female', 'Femme'),
        ('other', 'Autre'),
    ]

    passengerid = models.CharField(max_length=7, unique=True, blank=True, null=True)
    username = models.CharField(max_length=150, unique=True)
    nom = models.CharField(max_length=255, default='Default Name')
    prenom = models.CharField(max_length=255, default='Default prenom')
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    type_utilisateur = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='etudiant')
    account_status = models.CharField(max_length=20, choices=ACCOUNT_STATUS_CHOICES, default='pending')
    sex = models.CharField(max_length=10, choices=SEX_CHOICES, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    telephone = models.CharField(max_length=20, blank=True, null=True)
    otp = models.CharField(max_length=6, blank=True, null=True)
    otp_created_at = models.DateTimeField(null=True, blank=True)
    email_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

   

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['passengerid'], name='unique_passengerid')
        ]

    def __str__(self):
        return f"{self.username} ({self.get_type_utilisateur_display()})"

    def save(self, *args, **kwargs):
        if not self.passengerid:
            self.passengerid = self.generate_passengerid()
        super().save(*args, **kwargs)

    def generate_passengerid(self):
        if self.nom and self.prenom:
            first_two_letters_of_nom = self.nom[:2].upper()
            first_letter_of_prenom = self.prenom[0].upper()
            random_letter = random.choice(string.ascii_uppercase)
            random_digits = ''.join(random.choices(string.digits, k=3))
            return f"{first_two_letters_of_nom}{first_letter_of_prenom}{random_letter}{random_digits}"
        return ''

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

    def is_otp_valid(self):
        if self.otp_created_at:
            return self.otp_created_at >= timezone.now() - timedelta(minutes=10)
        return False


    
    
class SystemUser(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(_('email address'), unique=True)
    nom = models.CharField(max_length=255)
    prenom = models.CharField(max_length=255)
    telephone = models.CharField(max_length=20)

    ROLE_CHOICES = [
        ('administrator', 'Administrateur'),
        ('receptionist', 'Réceptionniste'),
        ('driver', 'Chauffeur'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = SystemUserManager()

    USERNAME_FIELD = 'username'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = ['email', 'nom', 'prenom', 'role']

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

    def get_full_name(self):
        return f"{self.prenom} {self.nom}"

    def get_short_name(self):
        return self.prenom
    
class CardInfo(models.Model):
    # Identifiant unique de la carte (UID)
    card_uid = models.CharField(max_length=50, unique=True)

    # Clé d'authentification (chiffrée)
    authentication_key_encrypted = models.BinaryField()

    # Code secret (chiffré)
    secret_code_encrypted = models.BinaryField()

    # Secteur sur lequel le système va enregistrer (par défaut le secteur 8)
    sector = models.IntegerField(default=8)

    # Type d'abonnement
    

    # Date d'expiration de la carte
    expiration_date = models.DateField()
    
    card_assignment = models.ForeignKey(
        CardAssignmentid,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='+',
        help_text="L'attribution de carte associée à cette carte."
    )


    def __str__(self):
        return f"Carte {self.card_uid}"

    # Initialiser l'objet Fernet avec la clé de chiffrement
    @property
    def fernet(self):
        return Fernet(settings.FERNET_KEY)

    # Méthodes pour gérer la clé d'authentification
    def set_authentication_key(self, raw_key):
        """
        Chiffre la clé d'authentification avant de la stocker.
        """
        self.authentication_key_encrypted = self.fernet.encrypt(raw_key.encode())

    def get_authentication_key(self):
        """
        Déchiffre la clé d'authentification pour l'utiliser.
        """
        return self.fernet.decrypt(self.authentication_key_encrypted).decode()

    # Méthodes pour gérer le code secret
    def set_secret_code(self, raw_secret_code):
        """
        Chiffre le code secret avant de le stocker.
        """
        self.secret_code_encrypted = self.fernet.encrypt(raw_secret_code.encode())

    def get_secret_code(self):
        """
        Déchiffre le code secret pour l'utiliser.
        """
        return self.fernet.decrypt(self.secret_code_encrypted).decode()
    
    
    
class PassengerCard(models.Model):
    passenger_user = models.ForeignKey(PassengerUser, on_delete=models.CASCADE)
    card_info = models.ForeignKey(CardInfo, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.passenger_user.username} - Carte {self.card_info.card_uid}"




class Subscription(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Cash'),
        ('moncash', 'MonCash Digicel'),
        ('natcash', 'NatCash Natcom'),
        ('credit_card', 'Carte de Crédit/Débit'),
        # Ajoutez d'autres méthodes de paiement si nécessaire
    ]

    RENEWAL_TYPE_CHOICES = [
        ('auto', 'Automatique'),
        ('manual', 'Manuel'),
    ]

    # Relation avec PassengerUser
    passenger_user = models.ForeignKey(PassengerUser, on_delete=models.CASCADE)
    
    # Informations sur le type d'abonnement
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.CASCADE, null=True, blank=True)
    
    payment_method = models.CharField(max_length=50, choices=PAYMENT_METHOD_CHOICES, default='cash')
    renewal_type = models.CharField(max_length=50, choices=RENEWAL_TYPE_CHOICES, default='manual')
    start_date = models.DateField(default=timezone.now)
    end_date = models.DateField()
    is_active = models.BooleanField(default=True)
    auto_renew = models.BooleanField(default=False)
    payment_received = models.BooleanField(default=False)  # Vérifie si le paiement a été reçu

    def __str__(self):
        return f"{self.passenger_user.username} - {self.subscription_type}"

    def renew(self, additional_days):
        """
        Renouvelle l'abonnement en prolongeant la date de fin.
        """
        self.end_date += timezone.timedelta(days=additional_days)
        self.save()
            
    def is_expired(self):
        """
        Vérifie si l'abonnement est expiré.
        """
        return self.end_date < timezone.now().date()


class Transaction(models.Model):
    TRANSACTION_TYPE_CHOICES = [
        ('card_creation', 'Création de carte'),
        # Vous pouvez ajouter d'autres types de transactions si nécessaire
    ]

    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Cash'),
        ('moncash', 'MonCash Digicel'),
        ('natcash', 'NatCash Natcom'),
        ('credit_card', 'Carte de Crédit/Débit'),
        # Ajoutez d'autres méthodes de paiement si nécessaire
    ]

    passenger_user = models.ForeignKey(PassengerUser, on_delete=models.CASCADE)
    transaction_type = models.CharField(max_length=50, choices=TRANSACTION_TYPE_CHOICES)
    payment_method = models.CharField(max_length=50, choices=PAYMENT_METHOD_CHOICES, default='cash')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_date = models.DateTimeField(default=timezone.now)
    is_successful = models.BooleanField(default=True)
    details = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Transaction {self.get_transaction_type_display()} pour {self.passenger_user.username} le {self.transaction_date.strftime('%Y-%m-%d')}"



class TravelTransaction(models.Model):
    passenger_user = models.ForeignKey(PassengerUser, on_delete=models.CASCADE)
    card_info = models.ForeignKey(CardInfo, on_delete=models.CASCADE)
    transaction_date = models.DateTimeField(default=timezone.now)
    is_approved = models.BooleanField()
    reason = models.CharField(max_length=255, blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    processed_by = models.ForeignKey(SystemUser, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        status = "Approuvé" if self.is_approved else "Refusé"
        return f"Voyage {status} pour {self.passenger_user.username} le {self.transaction_date.strftime('%Y-%m-%d %H:%M:%S')}"
    
    
    
class CardConfiguration(models.Model):
    CONFIGURATION_TYPE_CHOICES = [
        ('default', 'Défaut'),
        ('custom', 'Personnalisé'),
    ]

    name = models.CharField(max_length=100, unique=True)
    configuration_type = models.CharField(max_length=20, choices=CONFIGURATION_TYPE_CHOICES, default='default')
    authentication_key_encrypted = models.BinaryField()
    sector = models.IntegerField(default=8)
    access_bits_encrypted = models.BinaryField(blank=True, null=True)
    trailer_block_encrypted = models.BinaryField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Configuration {self.name}"

    @property
    def fernet(self):
        return Fernet(settings.FERNET_KEY)

    def set_authentication_key(self, raw_key):
        self.authentication_key_encrypted = self.fernet.encrypt(raw_key.encode())

    def get_authentication_key(self):
        return self.fernet.decrypt(self.authentication_key_encrypted).decode()

    def set_access_bits(self, raw_access_bits):
        self.access_bits_encrypted = self.fernet.encrypt(raw_access_bits.encode())

    def get_access_bits(self):
        if self.access_bits_encrypted:
            return self.fernet.decrypt(self.access_bits_encrypted).decode()
        return None

    def set_trailer_block(self, raw_trailer_block):
        self.trailer_block_encrypted = self.fernet.encrypt(raw_trailer_block.encode())

    def get_trailer_block(self):
        if self.trailer_block_encrypted:
            return self.fernet.decrypt(self.trailer_block_encrypted).decode()
        return None
    
    

    
    
class UnassignedCard(models.Model):
    CARD_TYPE_CHOICES = [
        ('MIFARE Classic 1K', 'MIFARE Classic 1K'),
        ('MIFARE Classic 4K', 'MIFARE Classic 4K'),
        ('MIFARE Ultralight', 'MIFARE Ultralight'),
        # Ajoutez d'autres types de cartes si nécessaire
    ]

    card_uid = models.CharField(max_length=50, unique=True)
    card_type = models.CharField(max_length=50, choices=CARD_TYPE_CHOICES)
    added_date = models.DateTimeField(auto_now_add=True)
    is_assigned = models.BooleanField(default=False)

    # Informations sur les accès
    available_sectors = models.JSONField(blank=True, null=True)
    default_authentication_key_encrypted = models.BinaryField(blank=True, null=True)

    def __str__(self):
        return f"Carte non attribuée UID: {self.card_uid}"

    @property
    def fernet(self):
        return Fernet(settings.FERNET_KEY)

    def set_default_authentication_key(self, raw_key):
        self.default_authentication_key_encrypted = self.fernet.encrypt(raw_key.encode())

    def get_default_authentication_key(self):
        if self.default_authentication_key_encrypted:
            return self.fernet.decrypt(self.default_authentication_key_encrypted).decode()
        return None
    
class CardOperation(models.Model):
    OPERATION_TYPE_CHOICES = [
        ('configure', 'Configuration'),
        ('change_security', 'Changement de sécurité'),
        ('erase', 'Effacement'),
        ('read', 'Lecture'),
        ('write', 'Écriture'),
        # Ajoutez d'autres types d'opérations si nécessaire
    ]

    card_info = models.ForeignKey(CardInfo, on_delete=models.CASCADE, null=True, blank=True)
    unassigned_card = models.ForeignKey(UnassignedCard, on_delete=models.CASCADE, null=True, blank=True)

    operation_type = models.CharField(max_length=50, choices=OPERATION_TYPE_CHOICES)
    configuration = models.ForeignKey(CardConfiguration, on_delete=models.SET_NULL, null=True, blank=True)
    performed_by = models.ForeignKey(SystemUser, on_delete=models.SET_NULL, null=True, blank=True)
    operation_date = models.DateTimeField(default=timezone.now)
    success = models.BooleanField(default=True)
    details = models.TextField(blank=True, null=True)

    def __str__(self):
        card_uid = self.card_info.card_uid if self.card_info else self.unassigned_card.card_uid
        return f"Opération {self.get_operation_type_display()} sur {card_uid} le {self.operation_date.strftime('%Y-%m-%d %H:%M:%S')}"

    def clean(self):
        """
        Validation pour s'assurer qu'une seule des deux cartes est renseignée.
        """
        if not self.card_info and not self.unassigned_card:
            raise ValidationError("Vous devez spécifier soit 'card_info', soit 'unassigned_card'.")
        if self.card_info and self.unassigned_card:
            raise ValidationError("Vous ne pouvez pas spécifier à la fois 'card_info' et 'unassigned_card'.")
        
        
class CardAssignment(models.Model):
    # Référence à la carte non attribuée
    unassigned_card = models.OneToOneField(
        UnassignedCard,
        on_delete=models.CASCADE,
        related_name='assignment'
    )
    
    # Référence à la carte attribuée
    card_info = models.OneToOneField(
        CardInfo,
        on_delete=models.CASCADE,
        related_name='assignment'
    )
    
    # Date d'attribution
    assigned_date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Assignée {self.card_info.card_uid} à partir de {self.unassigned_card.card_uid} le {self.assigned_date.strftime('%Y-%m-%d %H:%M:%S')}"
    
    def clean(self):
        """
        Validation pour s'assurer qu'une carte non attribuée n'est assignée qu'une seule fois.
        """
        if CardAssignment.objects.filter(unassigned_card=self.unassigned_card).exclude(id=self.id).exists():
            raise ValidationError("Cette carte non attribuée est déjà assignée.")
        if CardAssignment.objects.filter(card_info=self.card_info).exclude(id=self.id).exists():
            raise ValidationError("Cette carte attribuée est déjà liée à une autre carte non attribuée.")
        
        
class Parent(models.Model):
    student = models.ForeignKey(
        PassengerUser,
        on_delete=models.CASCADE,
        related_name='parent',
        limit_choices_to={'type_utilisateur': 'etudiant'}
    )
    nom_parent = models.CharField(max_length=255)

    class Meta:
        unique_together = ('student', 'nom_parent')

    def __str__(self):
        return f"Parent de {self.student.nom} {self.student.prenom}: {self.nom_parent}"

    
    

    
    
 