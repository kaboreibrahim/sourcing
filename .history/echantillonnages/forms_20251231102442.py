# echantillonnages/forms.py
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Field, Div
from django import forms
from echantillonnages.models import Echantionnage
from django.forms import TextInput, NumberInput, DateTimeInput

class EchantionnageForm(forms.ModelForm):

    commission = forms.DecimalField(
        label='Commission (1.5%)',
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'readonly': True,
            'step': '0.01'
        })
    )
    class Meta:
        model = Echantionnage
        fields = ['quantite', 'prix', 'date_creation']
        widgets = {
            'date_creation': DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'quantite': NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'prix': NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.commodite = kwargs.pop('commodite', None)
        super().__init__(*args, **kwargs)
        
        self.helper = FormHelper()
        self.helper.form_id = 'echantillon-form'
        self.helper.form_method = 'post'
        self.helper.form_action = 'echantillonnages:ajouter'
        
        # Ajouter des classes Bootstrap aux champs
        self.helper.layout = Layout(
            Div(
                Field('quantite', wrapper_class='mb-3'),
                Field('prix', wrapper_class='mb-3'),
                Field('date_creation', wrapper_class='mb-3'),
                css_class='modal-body'
            ),
            Div(
                Submit('submit', 'Enregistrer', css_class='btn btn-primary'),
                css_class='modal-footer'
            )
        )
        
    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.user and hasattr(self.user, 'fournisseur_profile'):
            instance.utilisateur = self.user
            instance.fournisseur = self.user.fournisseur_profile
        if self.commodite:
            instance.commodite = self.commodite
        if commit:
            instance.save()
        return instance