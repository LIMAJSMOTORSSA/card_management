from django import forms
from .models import PassengerUser, SubscriptionPlan, Subscription, PassengerUser, Parent
from django.core.exceptions import ValidationError
from django.utils import timezone
from dateutil.relativedelta import relativedelta


class AdminLoginForm(forms.Form):
    email = forms.EmailField(label="Adresse email", widget=forms.EmailInput(attrs={'class': 'form-control'}))
    password = forms.CharField(label="Mot de passe", widget=forms.PasswordInput(attrs={'class': 'form-control'}))


            
            
            
            
class PassengerUserForm(forms.ModelForm):
    confirm_password = forms.CharField(widget=forms.PasswordInput())
    nom_parent = forms.CharField(max_length=255, required=False)

    class Meta:
        model = PassengerUser
        fields = ['username', 'email', 'password', 'nom', 'prenom', 'type_utilisateur', 'sex', 'date_of_birth', 'address', 'telephone']
        widgets = {
            'password': forms.PasswordInput(),
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        type_utilisateur = cleaned_data.get("type_utilisateur")
        nom_parent = cleaned_data.get("nom_parent")

        if password != confirm_password:
            raise forms.ValidationError("Les mots de passe ne correspondent pas.")

        if type_utilisateur == 'etudiant' and not nom_parent:
            raise forms.ValidationError("Le nom du parent est requis pour les étudiants.")

        return cleaned_data

        
        

    
    
class UserSearchForm(forms.Form):
    search_query = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Nom, prénom ou ID du passager'})
    )

class SubscriptionSelectionForm(forms.Form):
    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Cash'),
        ('moncash', 'MonCash Digicel'),
        ('natcash', 'NatCash Natcom'),
        ('credit_card', 'Carte de Crédit/Débit'),
    ]

    selected_plans = forms.MultipleChoiceField(
        widget=forms.CheckboxSelectMultiple,
        required=True
    )
    payment_method = forms.ChoiceField(
        choices=PAYMENT_METHOD_CHOICES,
        required=True,
        widget=forms.RadioSelect
    )

    def __init__(self, *args, **kwargs):
        available_plans = kwargs.pop('available_plans', None)
        super().__init__(*args, **kwargs)
        if available_plans:
            self.fields['selected_plans'].choices = [(str(plan.id), str(plan)) for plan in available_plans]

class CheckoutForm(forms.Form):
    discount = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={'step': '0.01'})
    )

    def clean_discount(self):
        discount = self.cleaned_data['discount']
        if discount is None:
            return 0
        return discount
    
class EmailForm(forms.Form):
    email = forms.EmailField(required=True)