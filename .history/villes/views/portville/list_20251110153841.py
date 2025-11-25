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
    template_name = 'portville/ville_port_list.html'
    context_object_name = 'liaisons'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = super().get_queryset().select_related('ville', 'port')
        
        # Filtrage par recherche
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(ville__nom__icontains=search_query) |
                Q(port__nom__icontains(search_query))
            )
        
        # Filtrage par ville
        ville_id = self.request.GET.get('ville')
        if ville_id:
            queryset = queryset.filter(ville_id=ville_id)
        
        # Filtrage par port
        port_id = self.request.GET.get('port')
        if port_id:
            queryset = queryset.filter(port_id=port_id)
        
        # Filtrage par pays
        pays_id = self.request.GET.get('pays')
        if pays_id:
            queryset = queryset.filter(ville__pays_id=pays_id)
        
        return queryset.order_by('ville__nom', 'port__nom')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Récupérer les paramètres de filtre
        context['search_query'] = self.request.GET.get('search', '')
        context['selected_ville'] = self.request.GET.get('ville', '')
        context['selected_port'] = self.request.GET.get('port', '')
        context['selected_pays'] = self.request.GET.get('pays', '')
        
        # Récupérer toutes les villes et ports pour les filtres
        context['villes'] = Ville.objects.filter(deleted__isnull=True).order_by('nom')
        context['ports'] = Port.objects.filter(deleted__isnull=True).order_by('nom')
        
        # Récupérer la liste des pays pour le filtre
        from pays.models import Pays
        context['pays_list'] = Pays.objects.filter(deleted__isnull=True).order_by('nom')
        
        # Compter le nombre total de liaisons
        context['total_liaisons'] = self.get_queryset().count()
        
        return context