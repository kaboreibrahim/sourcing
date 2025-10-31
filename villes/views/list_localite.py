from django.views.generic import ListView 
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.db.models import Count, Q, Prefetch
from django.contrib.auth.mixins import LoginRequiredMixin
from zones.models import Zone
from  villes.models import Ville,Localite
 

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
        queryset = Localite.objects.select_related('ville').order_by(
            'ville__nom',
            'nom'
        )
        
        # Filtre de recherche
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(nom__icontains=search_query) |
                Q(ville__nom__icontains=search_query)
            )   
        
        # Filtre par ville
        ville_id = self.request.GET.get('ville', '')
        if ville_id:
            queryset = queryset.filter(ville_id=ville_id)
        
        # Filtre par zone
        zone_id = self.request.GET.get('zone', '')
        if zone_id:
            queryset = queryset.filter(ville__zone_id=zone_id)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        context['villes'] = Ville.objects.all().order_by('nom')
        context['selected_ville'] = self.request.GET.get('ville', '')
        context['zones'] = Zone.objects.all().order_by('numero')
        context['selected_zone'] = self.request.GET.get('zone', '')
        context['total_localites'] = Localite.objects.count()
        return context
