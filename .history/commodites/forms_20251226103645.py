from django import forms
from .models import FournisseurCommodite

class FournisseurCommoditeForm(forms.ModelForm):
    """
    Formulaire pour la mise à jour de la disponibilité d'une commodité par un fournisseur
    """
    class Meta:
        model = FournisseurCommodite
        fields = ['quantite_disponible', 'prix_unitaire', 'disponibilite', 'commentaire']
        labels = {
            'quantite_disponible': 'Quantité disponible (tonnes)',
            'prix_unitaire': 'Prix unitaire (FCFA/tonne)',
            'disponibilite': 'Disponibilité',
            'commentaire': 'Commentaire (facultatif)'
        }
        widgets = {
            'quantite_disponible': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'step': '0.01',
                'required': True
            }),
            'prix_unitaire': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'step': '1',
                'required': True
            }),
            'disponibilite': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'commentaire': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Ajoutez des détails sur la disponibilité...'
            })
        }
    
    def clean_quantite_disponible(self):
        quantite = self.cleaned_data.get('quantite_disponible')
        if quantite is not None and quantite < 0:
            raise forms.ValidationError("La quantité ne peut pas être négative.")
        return quantite
    
    def clean_prix_unitaire(self):
        prix = self.cleaned_data.get('prix_unitaire')
        if prix is not None and prix < 0:
            raise forms.ValidationError("Le prix unitaire ne peut pas être négatif.")
        return prix
