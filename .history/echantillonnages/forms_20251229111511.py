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
        fields = ['quantite', 'prix']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Ajouter'))
