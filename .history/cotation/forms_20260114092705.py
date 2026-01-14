from django import forms
from .models import DemandeCotation


class DemandeCotationForm(forms.ModelForm):
    class Meta:
        model = DemandeCotation
        fields = [
            'nom_client',
            'contact',
            'mail',
            'commodite',
            'quantite',
            'type_conditionnement',
            'incoterm',
            'pol',
            'pod',
            'target_price',
        ]

        widgets = {
            'nom_client': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nom du client ou société'
            }),
            'contact': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Téléphone'
            }),
            'mail': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Email'
            }),
            'commodite': forms.Select(attrs={
                'class': 'form-control'
            }),
            'quantite': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Quantité'
            }),
            'type_conditionnement': forms.Select(attrs={
                'class': 'form-control'
            }),
            'incoterm': forms.Select(attrs={
                'class': 'form-control'
            }),
            'pol': forms.Select(attrs={
                'class': 'form-control'
            }),
            'pod': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Port de déchargement (POD)'
            }),
            'target_price': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Target price'
            }),
        }

    def clean_quantite(self):
        quantite = self.cleaned_data.get('quantite')
        if quantite <= 0:
            raise forms.ValidationError("La quantité doit être supérieure à zéro.")
        return quantite

    def clean_target_price(self):
        price = self.cleaned_data.get('target_price')
        if price <= 0:
            raise forms.ValidationError("Le prix cible doit être supérieur à zéro.")
        return price

