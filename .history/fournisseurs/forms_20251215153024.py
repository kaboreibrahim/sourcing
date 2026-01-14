# fournisseurs/forms.py

from django import forms
from .models import FournisseurPort

class FournisseurPortForm(forms.ModelForm):
    class Meta:
        model = FournisseurPort
        fields = ['fournisseur', 'port', 'distance']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Personnalisez les querysets si nécessaire
        self.fields['fournisseur'].queryset = Fournisseur.objects.filter(deleted__isnull=True)
        self.fields['port'].queryset = Port.objects.all().order_by('nom')