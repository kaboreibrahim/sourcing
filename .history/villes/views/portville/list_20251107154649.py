from django.views.generic import ListView
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.db.models import Count, Q, Prefetch
from django.contrib.auth.mixins import LoginRequiredMixin
from port.models import Port
from villes.models import VillePort, Ville


# ============================================================
# VUES POUR PORT-VILLE (Liaison)
# ============================================================

class VillePortListView(LoginRequiredMixin, ListView):
    """
    Vue pour afficher la liste des liaisons port-ville
    """
    model = VillePort
    template_name = 'ville_port_list.html'
    context_object_name = 'liaisons'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = VillePort.objects.select_related(
            'port',
            'ville',
            'ville__zone',
        ).filter(deleted__isnull=True).order_by(
            'ville__nom',
            'port__nom'
        )
        
        # Filtre de recherche
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(port__nom__icontains=search_query) |
                Q(ville__nom__icontains=search_query) |
                Q(ville__zone__nom__icontains=search_query)
            )
        
        # Filtre par port
        port_id = self.request.GET.get('port', '')
        if port_id:
            queryset = queryset.filter(port_id=port_id)
        
        # Filtre par zone
        zone_id = self.request.GET.get('zone', '')
        if zone_id:
            queryset = queryset.filter(ville__zone_id=zone_id)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        context['ports'] = Port.objects.all().order_by('nom')
        context['selected_port'] = self.request.GET.get('port', '')
        
        # Import Zone pour le filtre
        from zones.models import Zone
        context['zones'] = Zone.objects.all().order_by('numero')
        context['selected_zone'] = self.request.GET.get('zone', '')
        
        context['total_liaisons'] = VillePort.objects.filter(
            deleted__isnull=True
        ).count()
        
        return context

