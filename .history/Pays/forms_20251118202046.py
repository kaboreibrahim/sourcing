from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Pays

class PaysForm(forms.ModelForm):
    """
    Formulaire pour la création et la mise à jour d'un pays.
    """
    class Meta:
        model = Pays
        fields = ['nom', 'code', 'flag']
        labels = {
            'nom': _('Nom du pays'),
            'code': _('Code ISO (2 lettres)'),
            'flag': _('Drapeau du pays'),
        }
        help_texts = {
            'code': _('Code ISO à 2 lettres (ex: FR pour la France)'),
            'flag': _('Téléchargez une image du drapeau (format JPG, JPEG ou PNG)'),
        }
        widgets = {
            'nom': forms.TextInput(attrs={
                'class': 'form-input mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring focus:ring-blue-200 focus:ring-opacity-50',
                'placeholder': _('Ex: France, Sénégal, Côte d\'Ivoire...')
            }),
            'code': forms.TextInput(attrs={
                'class': 'form-input mt-1 block w-24 rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring focus:ring-blue-200 focus:ring-opacity-50 uppercase',
                'placeholder': 'FR',
                'maxlength': '2',
                'style': 'text-transform: uppercase;'
            }),
        }
    
    def clean_code(self):
        """Convertit le code en majuscules."""
        code = self.cleaned_data.get('code', '')
        return code.upper()
    
    def clean(self):
        cleaned_data = super().clean()
        # Vous pouvez ajouter des validations supplémentaires ici si nécessaire
        return cleaned_data
