from django.views.generic import CreateView, View
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from fournisseurs.forms import FournisseurPortForm
from port.models import Port
from fournisseurs.models import Fournisseur, FournisseurPort
from villes.models import Localite
 
# ============================================================
# VUES POUR LA PORTFOURNISSEUR CREATE
# ============================================================
# fournisseurs/views/port_fournisseur.py

class PortFournisseurCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    """
    Vue pour créer une nouvelle liaison fournisseur-port
    """
    model = FournisseurPort
    template_name = 'port_fournisseur_form.html'
    fields = ['fournisseur', 'port']
    success_message = _("La liaison a été créée avec succès")
    
    def get_success_url(self):
        return reverse_lazy('port-fournisseur-list')
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        
        # Si on a un fournisseur_id dans l'URL, on le sélectionne par défaut
        if 'fournisseur_id' in self.kwargs:
            fournisseur = get_object_or_404(Fournisseur, id=self.kwargs['fournisseur_id'])
            form.fields['fournisseur'].initial = fournisseur
            form.fields['fournisseur'].widget.attrs['disabled'] = True
            
            # Filtrer les ports du même pays que le fournisseur
            if hasattr(fournisseur, 'get_zone') and fournisseur.get_zone():
                pays = fournisseur.get_zone().pays
                form.fields['port'].queryset = Port.objects.filter(pays=pays)
        else:
            # Si pas de fournisseur spécifié, on permet de le sélectionner
            form.fields['fournisseur'].queryset = Fournisseur.objects.filter(deleted__isnull=True)
        
        # Ajouter des attributs pour le chargement dynamique
        form.fields['port'].widget.attrs.update({
            'id': 'id_port',
            'class': 'form-control'
        })
        
        return form
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        fournisseur = None
        if 'fournisseur_id' in self.kwargs:
            fournisseur = get_object_or_404(Fournisseur, id=self.kwargs['fournisseur_id'])
            context['ports_lies'] = FournisseurPort.objects.filter(
                fournisseur=fournisseur
            ).select_related('port')
        
        context.update({
            'title': _("Ajouter une liaison port-fournisseur"),
            'button_text': _("Ajouter"),
            'fournisseur': fournisseur,
        })
        
        return context
        
    def form_valid(self, form):
        # If the form is valid but the supplier is disabled, we reactivate it
        if 'fournisseur' in form.cleaned_data and hasattr(form.fields['fournisseur'], 'widget') and 'disabled' in form.fields['fournisseur'].widget.attrs:
            form.instance.fournisseur = get_object_or_404(Fournisseur, id=self.kwargs.get('fournisseur_id', form.cleaned_data['fournisseur'].id))
        
        port = form.cleaned_data['port']
        fournisseur = form.instance.fournisseur
        
        # Check if the port is in the same country as the supplier
        if hasattr(fournisseur, 'zone') and fournisseur.zone and fournisseur.zone.pays != port.pays:
            form.add_error(
                None,
                _("Erreur: Le port %(port)s n'est pas dans le même pays que le fournisseur.") % {
                    'port': port.nom
                }
            )
            return self.form_invalid(form)

        # Check if the link already exists
        existing = FournisseurPort.objects.filter(
            fournisseur=fournisseur,
            port=port,
            deleted__isnull=True
        ).exists()
        
        if existing:
            form.add_error(None, _("Une liaison existe déjà entre ce fournisseur et ce port."))
            return self.form_invalid(form)
        
        # If distance is not provided, try to calculate it
        if not form.cleaned_data.get('distance'):
            try:
                # Try to calculate distance using geopy if coordinates are available
                if (hasattr(fournisseur, 'zone') and fournisseur.zone and 
                    hasattr(port, 'latitude') and port.latitude and 
                    hasattr(port, 'longitude') and port.longitude):
                    
                    from geopy.distance import geodesic
                    port_coords = (port.latitude, port.longitude)
                    fournisseur_coords = (fournisseur.zone.latitude, fournisseur.zone.longitude)
                    distance = geodesic(port_coords, fournisseur_coords).kilometers
                    form.instance.distance = round(distance, 2)
            except Exception as e:
                # If calculation fails, distance will remain None
                pass

        return super().form_valid(form)