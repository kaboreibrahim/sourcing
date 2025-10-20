from django.views.generic import ListView
from django.utils.translation import gettext_lazy as _
from django.db.models import Count, Q, Prefetch
from django.contrib.auth.mixins import LoginRequiredMixin
from zones.models import Zone
from  villes.models import Ville


# ============================================================
# VUES POUR ZONE
# ============================================================

class ZoneListView(LoginRequiredMixin, ListView):
    """
    Vue pour afficher la liste des zones sous forme de cards
    """
    model = Zone
    template_name = 'zone_list.html'
    context_object_name = 'zones'
    paginate_by = 12
    
    def get_queryset(self):
        """
        Optimisation avec annotation du nombre de villes
        et prefetch de la ville de référence
        """
        queryset = Zone.objects.annotate(
            total_villes=Count('villes', filter=Q(villes__deleted__isnull=True))
        ).prefetch_related(
            Prefetch(
                'villes',
                queryset=Ville.objects.filter(
                    est_ville_reference=True,
                    deleted__isnull=True
                ),
                to_attr='ville_ref'
            )
        ).order_by('numero')
        
        # Filtre de recherche
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(numero__icontains=search_query) |
                Q(description__icontains=search_query)|
                Q(villes__icontains=search_query)
            )
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        context['total_zones'] = Zone.objects.count()
        return context
