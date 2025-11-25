from django.views.generic import ListView 
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.db.models import Count, Q, Prefetch
from django.contrib.auth.mixins import LoginRequiredMixin
from zones.models import Zone
from Pays.models import Pays
from villes.models import Ville,VillePort


# ============================================================
# VUES POUR LA LISTE DES VILLES
# ============================================================

class VilleListView(LoginRequiredMixin, ListView):
    """
    Vue pour afficher la liste de toutes les villes
    """
    model = Ville
    template_name = 'ville/ville_list.html'
    context_object_name = 'villes'
    paginate_by = 20
        
    def get_queryset(self):
        queryset = Ville.objects.select_related('zone', 'zone__pays').order_by(
            'zone__pays__nom',  # Tri par pays via la zone
            'zone__numero',
            'nom'
        ).prefetch_related('ville_ports')
        
        # Filtre de recherche
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(nom__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(zone__numero__icontains=search_query) |
                Q(zone__pays__nom__icontains=search_query)  # Recherche par nom de pays via la zone
            )
        
        # Filtre par zone
        zone_id = self.request.GET.get('zone', '')
        if zone_id:
            queryset = queryset.filter(zone_id=zone_id)
            
        # Filtre par pays via la zone
        pays_id = self.request.GET.get('pays', '')
        if pays_id:
            queryset = queryset.filter(zone__pays_id=pays_id)
        
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        context['zones'] = Zone.objects.all().order_by('numero')
        context['pays_list'] = Pays.objects.all().order_by('nom')  # Ajout de la liste des pays
        context['selected_zone'] = self.request.GET.get('zone', '')
        context['selected_pays'] = self.request.GET.get('pays', '')
        context['total_villes'] = Ville.objects.count()
        return context
