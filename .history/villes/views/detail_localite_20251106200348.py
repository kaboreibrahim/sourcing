from django.views.generic import DetailView
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.mixins import LoginRequiredMixin
from zones.models import Zone
from villes.models import Localite    

# ============================================================
# VUES POUR LES DETAILS DES LOCALITES
# ============================================================
class LocaliteDetailView(LoginRequiredMixin, DetailView):
    """
    Vue pour afficher les détails d'une localité avec ses ports
    """
    model = Localite
    template_name = 'localite/localite_detail.html'
    context_object_name = 'localite'
    
    def get_queryset(self):
        """
        Optimise les requêtes en chargeant la ville, la zone et les ports en une seule requête
        """
        return Localite.objects.select_related(
            'ville', 
            'ville__zone'
        ).prefetch_related(
            'ports_localites__port'  # Précharge les relations PortLocalite et Port
        )
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Récupérer les ports liés à la localité avec leurs distances
        context['localite_ports'] = self.object.ports_localites.select_related('port').all().order_by('port__nom')
        context['nombre_ports'] = context['localite_ports'].count()
        
        return context