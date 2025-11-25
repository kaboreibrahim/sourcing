from django.views.generic import ListView 
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.db.models import Count, Q, Prefetch
from django.contrib.auth.mixins import LoginRequiredMixin
from zones.models import Zone
from villes.models import Ville, Localite, PortLocalite
from Pays.models import Pays
 

# ============================================================
# VUES POUR LA LISTE DES localite
# ============================================================

class LocaliteListView(LoginRequiredMixin, ListView):
    """
    Vue pour afficher la liste de toutes les localites
    """
    model = Localite
    template_name = 'localite/localite_list.html'
    context_object_name = 'localites'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Localite.objects.select_related(
            'ville', 
            'ville__zone',
            'ville__zone__pays'  # Accès au pays via la zone
        ).prefetch_related(
            Prefetch(
                'ports_localites',
                queryset=PortLocalite.objects.select_related('port').order_by('port__nom')
            )
        ).order_by(
            'ville__zone__pays__nom',  # Tri par pays via la zone
            'ville__zone__numero',
            'ville__nom',
            'nom'
        )
        
        # Filtre de recherche
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(nom__icontains=search_query) |
                Q(ville__nom__icontains=search_query) |
                Q(ville__zone__pays__nom__icontains=search_query)  # Recherche par pays via la zone
            )   
        
        # Filtre par ville
        ville_id = self.request.GET.get('ville', '')
        if ville_id:
            queryset = queryset.filter(ville_id=ville_id)
        
        # Filtre par zone
        zone_id = self.request.GET.get('zone', '')
        if zone_id:
            queryset = queryset.filter(ville__zone_id=zone_id)
            
        # Filtre par pays via la zone
        pays_id = self.request.GET.get('pays', '')
        if pays_id:
            queryset = queryset.filter(ville__zone__pays_id=pays_id)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        context['villes'] = Ville.objects.all().order_by('nom')
        context['selected_ville'] = self.request.GET.get('ville', '')
        context['zones'] = Zone.objects.all().order_by('numero')
        context['selected_zone'] = self.request.GET.get('zone', '')
        context['pays_list'] = Pays.objects.all().order_by('nom')
        context['selected_pays'] = self.request.GET.get('pays', '')
        context['total_localites'] = Localite.objects.count()
        return context
