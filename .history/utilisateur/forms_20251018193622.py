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
