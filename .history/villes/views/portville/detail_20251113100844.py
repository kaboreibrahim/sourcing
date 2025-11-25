from django.views.generic import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from villes.models import VillePort
import json


class VillePortDetailView(LoginRequiredMixin, DetailView):
    """
    Vue pour afficher les détails d'une liaison port-ville avec une carte Mapbox
    """
    model = VillePort
    template_name = 'portville/ville_port_detail.html'
    context_object_name = 'ville_port'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ville_port = self.get_object()
        
        # Récupérer les coordonnées
        port = ville_port.port
        ville = ville_port.ville
        
        # Titre traduit
        title = str(_("Liaison {port} - {ville}").format(
            port=port.nom, 
            ville=ville.nom
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
            'ville': {
                'nom': ville.nom,
                'latitude': float(ville.latitude) if ville.latitude is not None else None,
                'longitude': float(ville.longitude) if ville.longitude is not None else None
            },
            'distance': float(ville_port.distance) if ville_port.distance is not None else None
        }
        
        # Ajouter au contexte
        context.update({
            'title': title,
            'map_data_json': map_data,  # Django json_script va gérer la sérialisation
            'port': port,
            'ville': ville,
            'distance': map_data['distance']
        })
            
        return context