import random
from django.core.exceptions import ValidationError
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row,Column
from django.core.mail import send_mail
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.forms import modelformset_factory
from django import forms
from django.forms import  DateTimeInput



#formulaire de connexion
class LoginForm(AuthenticationForm): 
    
    username = forms.CharField(
        max_length=254,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom d\'utilisateur ou e-mail', 'id': 'username'})
    )
    password = forms.CharField(
        label="Mot de passe",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Mot de passe', 'id': 'password'})
    )


# 2ath

class TwoFactorMethodForm(forms.Form):
    two_factor_method = forms.ChoiceField(
        choices=[
            ('email', 'Receive Code by Email'),
            ('google_auth', 'Use Google Authenticator')
        ],
        widget=forms.RadioSelect,
        label="Choisissez la méthode de deux facteurs"
    )

class EmailVerificationForm(forms.Form):
    code = forms.CharField(
        max_length=6,
        widget=forms.TextInput(attrs={'placeholder': 'Entrez le code'})
    )

class GoogleAuthVerificationForm(forms.Form):
    code = forms.CharField(
        max_length=6,
        widget=forms.TextInput(attrs={'placeholder': 'Entrez le code Google Authenticator'})
    )


