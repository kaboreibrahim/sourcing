from django import forms
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _
from .models import DemandeCotation

class DemandeCotationForm(forms.ModelForm):
    contact = forms.CharField(
        label='Téléphone',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ex: +225 07 00 00 00 00',
            'pattern': '^\+?[\d\s-]{10,}$',
            'title': 'Format: +225 07 00 00 00 00 ou 07 00 00 00 00',
            'minlength': '10',
            'maxlength': '20'
        }),
        help_text='Format: +225 07 00 00 00 00 ou 07 00 00 00 00'
    )
    
    mail = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'votre@email.com',
            'pattern': '[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}$',
            'title': 'Entrez une adresse email valide'
        })
    )
    
    quantite = forms.DecimalField(
        label='Quantité',
        min_value=0.01,
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': '0.00',
            'step': '0.01',
            'min': '0.01'
        })
    )
    
    target_price = forms.DecimalField(
        label='Prix cible',
        required=False,
        min_value=0.01,
        max_digits=12,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': '0.00',
            'step': '0.01',
            'min': '0.01'
        })
    )

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
                'placeholder': 'Nom du client ou société',
                'minlength': '2',
                'maxlength': '100',
                'pattern': '^[a-zA-ZÀ-ÿ\s\'-]+$',
                'title': 'Lettres, espaces, tirets et apostrophes uniquement'
            }),
            'commodite': forms.Select(attrs={
                'class': 'form-control',
                'required': 'required'
            }),
            'type_conditionnement': forms.Select(attrs={
                'class': 'form-control',
                'required': 'required'
            }),
            'incoterm': forms.Select(attrs={
                'class': 'form-control',
                'required': 'required'
            }),
            'pol': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Port de chargement (POL)',
                'minlength': '2',
                'maxlength': '100'
            }),
            'pod': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Port de déchargement (POD)',
                'minlength': '2',
                'maxlength': '100'
            }),
        }
        error_messages = {
            'nom_client': {
                'required': _('Le nom du client est obligatoire'),
                'max_length': _('Le nom ne peut pas dépasser 100 caractères')
            },
            'mail': {
                'required': _('L\'adresse email est obligatoire'),
                'invalid': _('Veuillez entrer une adresse email valide')
            },
            'quantite': {
                'required': _('La quantité est obligatoire'),
                'min_value': _('La quantité doit être supérieure à zéro')
            },
            'target_price': {
                'min_value': _('Le prix doit être supérieur à zéro')
            }
        }

    def clean_contact(self):
        contact = self.cleaned_data.get('contact')
        # Nettoyer le numéro de téléphone
        contact = re.sub(r'[^\d+]', '', contact)
        
        # Vérifier la longueur minimale (au moins 10 chiffres)
        if len(contact) < 10:
            raise forms.ValidationError(
                _('Le numéro de téléphone doit contenir au moins 10 chiffres')
            )
            
        # Vérifier le format international
        if contact.startswith('225'):
            contact = '+' + contact
        elif not contact.startswith('+225'):
            contact = '+225' + contact.lstrip('0')
            
        return contact
        
    def clean_nom_client(self):
        nom_client = self.cleaned_data.get('nom_client', '').strip()
        if not nom_client:
            raise forms.ValidationError(_('Le nom du client est obligatoire'))
        if len(nom_client) < 2:
            raise forms.ValidationError(_('Le nom est trop court'))
        return nom_client
        
    def clean(self):
        cleaned_data = super().clean()
        pol = cleaned_data.get('pol')
        pod = cleaned_data.get('pod')
        incoterm = cleaned_data.get('incoterm')
        
        # Vérification cohérence des ports et incoterm
        if incoterm and incoterm.code in ['FOB', 'CFR', 'CIF'] and not pol:
            self.add_error('pol', _('Le port de chargement est obligatoire pour cet incoterm'))
            
        if incoterm and incoterm.code in ['CFR', 'CIF'] and not pod:
            self.add_error('pod', _('Le port de déchargement est obligatoire pour cet incoterm'))
            
        return cleaned_data
