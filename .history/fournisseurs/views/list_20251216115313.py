from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.db.models import Count, Q, Prefetch
from django.contrib.auth.mixins import LoginRequiredMixin
from fournisseurs.models import Fournisseur
from commodites.models import FournisseurCommodite, Commodite
from zones.models import Zone
from villes.models import Ville
from Pays.models import Pays

# ============================================================
# VUES POUR FOURNISSEUR
# ============================================================

class FournisseurListView(LoginRequiredMixin, ListView):
    """
    Vue pour afficher la liste des fournisseurs sous forme de cards
    """
    model = Fournisseur
    template_name = 'fournisseur_list.html'
    context_object_name = 'fournisseurs'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = Fournisseur.objects.select_related(
            'ville',
            'ville__zone'
        ).annotate(
            total_commodites=Count(
                'liens_commodites',
                filter=Q(liens_commodites__deleted__isnull=True)
            )
        ).prefetch_related(
            Prefetch(
                'liens_commodites',
                queryset=FournisseurCommodite.objects.select_related('commodite').filter(
                    deleted__isnull=True
                )
            )
        ).order_by('nom')
        
        # Search filter
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(nom__icontains=search_query) |
                Q(telephone__icontains=search_query) |
                Q(email__icontains=search_query)
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
            villes = villes.filter(zone__pays_id=context['selected_pays'])
        context['villes'] = villes.order_by('nom')
        
        context['total_fournisseurs'] = Fournisseur.objects.count()
        return context


class FournisseurZoneListAPI(View):
    def get(self, request):
        pays_id = request.GET.get('pays_id')
        zones = Zone.objects.all()
        
        if pays_id:
            zones = zones.filter(pays_id=pays_id)
            
        data = [{
            'id': str(zone.id),
            'numero': zone.numero
        } for zone in zones]
        
        return JsonResponse(data, safe=False)
class FournisseurVilleListAPI(View):
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