from django.views.generic import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from fournisseurs.models import FournisseurPort
import json


class PortFournisseurDetailView(LoginRequiredMixin, DetailView):
    """
    Vue pour afficher les détails d'une liaison port-localite avec une carte Mapbox
    """
    model = FournisseurPort
    template_name = 'port_fournisseur_detail.html'
    context_object_name = 'fournisseur_port'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        fournisseur_port = self.get_object()
        
        # Récupérer les coordonnées
        port = fournisseur_port.port
        fournisseur = fournisseur_port.fournisseur
        
        # Titre traduit
        title = str(_("Liaison {port} - {fournisseur}").format(
            port=port.nom, 
            fournisseur=fournisseur.nom
        ))
        
        # Préparer les données pour la carte (dictionnaire Python)
        map_data = {
            'mapbox_token': getattr(
                settings, 
                'MAPBOX_ACCESS_TOKEN', 
                'pk.eyJ1IjoiaWJyYWsiLCJhIjoiY21oYnV4M3M5MDZqMTJyc2E0enFpbTlwaCJ9.OH_RYh--XO3vn363pKRlRg'
            ),
            'port': {
                'nom': port.nom,
                'latitude': float(port.latitude) if port.latitude is not None else None,
                'longitude': float(port.longitude) if port.longitude is not None else None
            },
            'fournisseur': {
                'nom': fournisseur.nom,
                'latitude': float(fournisseur.latitude) if fournisseur.latitude is not None else None,
                'longitude': float(fournisseur.longitude) if fournisseur.longitude is not None else None
            },
            'distance': float(fournisseur_port.distance) if fournisseur_port.distance is not None else None
        }
        
        # Ajouter au contexte
        context.update({
            'title': title,
            'map_data_json': map_data,  # Django json_script va gérer la sérialisation
            'port': port,
            'fournisseur': fournisseur,
            'distance': map_data['distance']
        })
            
        return context