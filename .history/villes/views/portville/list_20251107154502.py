from django.views.generic import ListView
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.db.models import Count, Q, Prefetch
from django.contrib.auth.mixins import LoginRequiredMixin
from port.models import Port
from ville.


# ============================================================
# VUES POUR FOURNISSEUR-COMMODITE (Liaison)
# ============================================================

class FournisseurCommoditeListView(LoginRequiredMixin, ListView):
    """
    Vue pour afficher la liste des liaisons fournisseur-commodité
    """
    model = FournisseurCommodite
    template_name = 'fournisseur_commodite_list.html'
    context_object_name = 'liaisons'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = FournisseurCommodite.objects.select_related(
            'fournisseur',
            'fournisseur__ville',
            'fournisseur__ville__zone',
            'commodite'
        ).filter(deleted__isnull=True).order_by(
            'commodite__nom',
            'fournisseur__nom'
        )
        
        # Filtre de recherche
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(fournisseur__nom__icontains=search_query) |
                Q(commodite__nom__icontains=search_query) |
                Q(fournisseur__ville__nom__icontains=search_query)
            )
        
        # Filtre par commodité
        commodite_id = self.request.GET.get('commodite', '')
        if commodite_id:
            queryset = queryset.filter(commodite_id=commodite_id)
        
        # Filtre par zone
        zone_id = self.request.GET.get('zone', '')
        if zone_id:
            queryset = queryset.filter(fournisseur__ville__zone_id=zone_id)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        context['commodites'] = Commodite.objects.all().order_by('nom')
        context['selected_commodite'] = self.request.GET.get('commodite', '')
        
        # Import Zone pour le filtre
        from zones.models import Zone
        context['zones'] = Zone.objects.all().order_by('numero')
        context['selected_zone'] = self.request.GET.get('zone', '')
        
        context['total_liaisons'] = FournisseurCommodite.objects.filter(
            deleted__isnull=True
        ).count()
        
        return context

