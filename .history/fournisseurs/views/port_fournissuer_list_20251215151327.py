# fournisseurs/views/port_fournissuer_list.py

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

class PortFournissuerListView(LoginRequiredMixin, ListView):
    """
    Vue pour afficher la liste des liaisons port-fournisseur
    """
    model = FournisseurPort
    template_name = 'port_fournisseur_list.html'
    context_object_name = 'liaisons'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = FournisseurPort.objects.select_related(
            'port',
            'port__pays',
            'fournisseur',
            'fournisseur__ville',
            'fournisseur__ville__zone'
        ).filter(deleted__isnull=True).order_by(
            'fournisseur__nom',
            'port__nom'
        )
        
        # Filtrage par recherche
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(port__nom__icontains=search_query) |
                Q(fournisseur__nom__icontains=search_query) |
                Q(fournisseur__ville__zone__numero__icontains(search_query))
            )

        # Filtrage par port
        port_id = self.request.GET.get('port', '')
        if port_id:
            queryset = queryset.filter(port_id=port_id)
        
        # Filtrage par zone
        zone_id = self.request.GET.get('zone', '')
        if zone_id:
            queryset = queryset.filter(fournisseur__ville__zone_id=zone_id)
            
        # Filtrage par fournisseur
        fournisseur_id = self.request.GET.get('fournisseur', '')
        if fournisseur_id:
            queryset = queryset.filter(fournisseur_id=fournisseur_id)
            
        # Filtrage par pays
        pays_id = self.request.GET.get('pays', '')
        if pays_id:
            queryset = queryset.filter(port__pays_id=pays_id)
        
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        
        # Liste des ports pour le filtre
        context['ports'] = Port.objects.all().order_by('nom')
        context['selected_port'] = self.request.GET.get('port', '')
        
        # Liste des zones pour le filtre
        context['zones'] = Zone.objects.all().order_by('numero')
        context['selected_zone'] = self.request.GET.get('zone', '')
        
        # Liste des fournisseurs pour le filtre
        context['fournisseurs'] = Fournisseur.objects.filter(
            deleted__isnull=True
        ).order_by('nom')
        context['selected_fournisseur'] = self.request.GET.get('fournisseur', '')
        
        # Liste des pays pour le filtre
        context['pays_list'] = Pays.objects.all().order_by('nom')
        context['selected_pays'] = self.request.GET.get('pays', '')
        
        # Nombre total de liaisons
        context['total_liaisons'] = FournisseurPort.objects.filter(
            deleted__isnull=True
        ).count()
        
        # URL pour le bouton de réinitialisation
        context['reset_url'] = reverse_lazy('port-fournisseur-list')
        
        return context