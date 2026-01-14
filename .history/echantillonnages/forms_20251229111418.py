from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django.forms import modelformset_factory
from django import forms
from django.forms import  DateTimeInput
from echantillonnages.models import Echantionnage
from commodites.models import Commodite

class EchantionnageForm(forms.ModelForm):
    class Meta:
        model = Echantionnage
        fields = ['nom', 'description', 'date_creation', 'date_fin', 'quantite', 'prix', 'commodite']
