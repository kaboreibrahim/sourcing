# fournisseurs/forms.py

from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import FournisseurPort, Fournisseur
from port.models import Port
from utilisateur.models import Utilisateur
from django.utils.translation import gettext_lazy as _
import get_user_model

class FournisseurPortForm(forms.ModelForm):
    class Meta:
        model = FournisseurPort
        fields = ['fournisseur', 'port', 'distance']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Personnalisez les querysets si nécessaire
        self.fields['fournisseur'].queryset = Fournisseur.objects.filter(deleted__isnull=True)
        self.fields['port'].queryset = Port.objects.all().order_by('nom')


class FournisseurUserCreationForm(UserCreationForm):
    """
    Formulaire pour créer un compte utilisateur pour un fournisseur
    """
    email = forms.EmailField(
        label=_("Adresse email"),
        max_length=254,
        help_text=_("Requis. Entrez une adresse email valide.")
    )
    
    class Meta:
        model = get_user_model()
        fields = ('username', 'email', 'password1', 'password2')
    
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Personnalisation des champs
        self.fields['username'].label = _("Nom d'utilisateur")
        self.fields['password1'].label = _("Mot de passe")
        self.fields['password2'].label = _("Confirmation du mot de passe")
    
    def save(self, fournisseur=None, commit=True):
        user = super().save(commit=False)
        user.type_user = 'FS'  # Type utilisateur Fournisseur
        user.is_active = True
        
        if fournisseur:
            user.first_name = fournisseur.nom_responsable or ''
            user.last_name = fournisseur.nom
            user.phone = fournisseur.contact or ''
        
        if commit:
            user.save()
            
            # Lier l'utilisateur au fournisseur
            if fournisseur:
                fournisseur.user = user
                fournisseur.save(update_fields=['user'])
                
        return user