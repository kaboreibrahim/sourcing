from django.views.generic import ListView
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.db.models import Count, Q, Prefetch
from django.contrib.auth.mixins import LoginRequiredMixin
from port.models import Port
from fournisseurs.models import Fournisseur, FournisseurPort
from zones.models import Zone
from Pays.models import Pays

# ============================================================
# VUES POUR PORT-FOURNISSUER (Liaison)
# ============================================================

class PortFournissuerListView(LoginRequiredMixin, ListView):
    """
    Vue pour afficher la liste des liaisons port-localite
    """
    model = FournisseurPort
    template_name = 'port_fournisseur_list.html'
    context_object_name = 'liaisons'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = FournisseurPort.objects.select_related(
            'port',
            'port__pays',  # For country filtering
            'localite',
            'localite__ville',  # Go through localite to get to ville
            'localite__ville__zone',  # Then from ville to zone
        ).filter(deleted__isnull=True).order_by(
            'localite__nom',
            'port__nom'
        )
        
        # Rest of your filtering code remains the same
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(port__nom__icontains=search_query) |
                Q(localite__nom__icontains=search_query) |
                Q(localite__ville__zone__numero__icontains=search_query)
            )

        port_id = self.request.GET.get('port', '')
        if port_id:
            queryset = queryset.filter(port_id=port_id)
        
        zone_id = self.request.GET.get('zone', '')
        if zone_id:
            queryset = queryset.filter(fournisseur__ville__zone_id=zone_id)
            
        # Country filter
        pays_id = self.request.GET.get('pays', '')
        if pays_id:
            queryset = queryset.filter(port__pays_id=pays_id)
        
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        context['ports'] = Port.objects.all().order_by('nom')
        context['selected_port'] = self.request.GET.get('port', '')
      
        context['zones'] = Zone.objects.all().order_by('numero')
        context['selected_zone'] = self.request.GET.get('zone', '')
        
        # Ajout des localites et pays au contexte
        context['localites'] = Fournisseur.objects.filter(deleted__isnull=True).order_by('nom')
        context['selected_localite'] = self.request.GET.get('localite', '')
        context['pays_list'] = Pays.objects.all().order_by('nom')
        context['selected_pays'] = self.request.GET.get('pays', '')
        
        context['total_liaisons'] = FournisseurPort.objects.filter(
            deleted__isnull=True
        ).count()
        
        return context