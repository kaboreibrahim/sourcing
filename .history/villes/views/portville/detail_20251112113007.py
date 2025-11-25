from django.views.generic import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from villes.models import VillePort

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
        
        # Préparer les données pour la carte
        context.update({
        'title': _("Détails de la liaison"),
        'mapbox_token': 'pk.eyJ1IjoiaWJyYWsiLCJhIjoiY21oYnV4M3M5MDZqMTJyc2E0enFpbTlwaCJ9.OH_RYh--XO3vn363pKRlRg',  # Token Mapbox
        'port': {
            'nom': port.nom,
            'latitude': port.latitude,
            'longitude': port.longitude,
        },
        'ville': {
            'nom': ville.nom,
            'latitude': ville.latitude,
            'longitude': ville.longitude,
        },
        'distance': ville_port.distance
        })
            
        return context
