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
        
        # In LocaliteListView
    def get_queryset(self):
        queryset = Localite.objects.select_related(
            'ville', 
            'ville__zone',
            'ville__zone__pays'
        ).prefetch_related(
            Prefetch(
                'ports_localites',
                queryset=PortLocalite.objects.select_related('port').order_by('port__nom')
            )
        ).order_by(
            'ville__zone__pays__nom',
            'ville__zone__numero',
            'ville__nom',
            'nom'
        )
        
        # Search filter
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(nom__icontains=search_query) |
                Q(ville__nom__icontains=search_query) |
                Q(ville__zone__pays__nom__icontains=search_query)
            )   
        
        # Apply filters
        selected_pays = self.request.GET.get('pays')
        if selected_pays:
            queryset = queryset.filter(ville__zone__pays_id=selected_pays)
            
        selected_zone = self.request.GET.get('zone')
        if selected_zone:
            queryset = queryset.filter(ville__zone_id=selected_zone)
            
        selected_ville = self.request.GET.get('ville')
        if selected_ville:
            queryset = queryset.filter(ville_id=selected_ville)
        
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        context['selected_pays'] = self.request.GET.get('pays', '')
        context['selected_zone'] = self.request.GET.get('zone', '')
        context['selected_ville'] = self.request.GET.get('ville', '')
        
        # Get all countries
        context['pays_list'] = Pays.objects.all().order_by('nom')
        
        # Get zones filtered by selected country
        zones = Zone.objects.all()
        if context['selected_pays']:
            zones = zones.filter(pays_id=context['selected_pays'])
        context['zones'] = zones.order_by('numero')
        
        # Get cities filtered by selected zone
        villes = Ville.objects.all()
        if context['selected_zone']:
            villes = villes.filter(zone_id=context['selected_zone'])
        elif context['selected_pays']:
            # If only country is selected, show all cities in that country
            villes = villes.filter(zone__pays_id=context['selected_pays'])
        context['villes'] = villes.order_by('nom')
        
        context['total_localites'] = Localite.objects.count()
        return context


from django.http import JsonResponse
from django.views import View
from villes.models import Ville

class LocaliteVilleListAPI(View):
    def get(self, request):
        zone_id = request.GET.get('zone_id')
        villes = Ville.objects.all()
        
        if zone_id:
            villes = villes.filter(zone_id=zone_id)
            
        data = [{
            'id': str(ville.id),
            'nom': ville.nom
        } for ville in villes]
        
        return JsonResponse(data, safe=False)