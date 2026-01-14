from django.views.generic import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from illes.models import PortFournisseur
import json


class PortFournisseurDetailView(LoginRequiredMixin, DetailView):
    """
    Vue pour afficher les détails d'une liaison port-localite avec une carte Mapbox
    """
    model = PortLocalite
    template_name = 'portlocalite/port_localite_detail.html'
    context_object_name = 'port_localite'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        port_localite = self.get_object()
        
        # Récupérer les coordonnées
        port = port_localite.port
        localite = port_localite.localite
        
        # Titre traduit
        title = str(_("Liaison {port} - {localite}").format(
            port=port.nom, 
            localite=localite.nom
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
            'localite': {
                'nom': localite.nom,
                'latitude': float(localite.latitude) if localite.latitude is not None else None,
                'longitude': float(localite.longitude) if localite.longitude is not None else None
            },
            'distance': float(port_localite.distance) if port_localite.distance is not None else None
        }
        
        # Ajouter au contexte
        context.update({
            'title': title,
            'map_data_json': map_data,  # Django json_script va gérer la sérialisation
            'port': port,
            'localite': localite,
            'distance': map_data['distance']
        })
            
        return context