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
        """
        Optimisation avec annotation du nombre de commodités
        """
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
        
        # Filtre de recherche
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(nom__icontains=search_query) |
                Q(nom_responsable__icontains=search_query) |
                Q(contact__icontains=search_query) |
                Q(localite__icontains=search_query) |
                Q(ville__nom__icontains=search_query)
            )
        
        # Filtre par zone
        zone_id = self.request.GET.get('zone', '')
        if zone_id:
            queryset = queryset.filter(ville__zone_id=zone_id)
        
        # Filtre par ville
        ville_id = self.request.GET.get('ville', '')
        if ville_id:
            queryset = queryset.filter(ville_id=ville_id)
        
        # Filtre par commodité
        commodite_id = self.request.GET.get('commodite', '')
        if commodite_id:
            queryset = queryset.filter(liens_commodites__commodite_id=commodite_id)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        context['total_fournisseurs'] = Fournisseur.objects.count()
        
        
        context['zones'] = Zone.objects.all().order_by('numero')
        context['selected_zone'] = self.request.GET.get('zone', '')
        
        context['villes'] = Ville.objects.select_related('zone').order_by('nom')
        context['selected_ville'] = self.request.GET.get('ville', '')
        
        context['commodites'] = Commodite.objects.all().order_by('nom')
        context['selected_commodite'] = self.request.GET.get('commodite', '')
        
        return context
