from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.db.models import Count, Q, Prefetch
from django.contrib.auth.mixins import LoginRequiredMixin
from fournisseurs.models import Fournisseur
from commodites.models import FournisseurCommodite, Commodite
from zones.models import Zone
from villes.models import Ville, Localite
 
# ============================================================
# VUE POUR RECHERCHE AVANCÉE
# ============================================================

class FournisseurSearchView(LoginRequiredMixin, ListView):
    """
    Vue pour la recherche avancée de fournisseurs
    """
    model = Fournisseur
    template_name = 'fournisseur_search.html'
    context_object_name = 'fournisseurs'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Fournisseur.objects.select_related(
            'ville',
            'ville__zone',
            'localite'
        ).annotate(
            total_commodites=Count('liens_commodites')
        )
        
        # Recherche par nom
        nom = self.request.GET.get('nom', '')
        if nom:
            queryset = queryset.filter(nom__icontains=nom)
        
        # Recherche par responsable
        responsable = self.request.GET.get('responsable', '')
        if responsable:
            queryset = queryset.filter(nom_responsable__icontains=responsable)
        
        # Filtre par zone
        zone_id = self.request.GET.get('zone', '')
        if zone_id:
            queryset = queryset.filter(ville__zone_id=zone_id)
        
        # Filtre par ville
        ville_id = self.request.GET.get('ville', '')
        if ville_id:
            queryset = queryset.filter(ville_id=ville_id)
        
         # Filtre par localite
        localite_id = self.request.GET.get('localite', '')
        if localite_id:
            queryset = queryset.filter(localite_id=localite_id)
        
        # Filtre par commodité
        commodite_id = self.request.GET.get('commodite', '')
        if commodite_id:
            queryset = queryset.filter(liens_commodites__commodite_id=commodite_id)
        
        # Filtre par présence de coordonnées GPS
        has_gps = self.request.GET.get('has_gps', '')
        if has_gps == 'yes':
            queryset = queryset.filter(
                latitude__isnull=False,
                longitude__isnull=False
            )
        elif has_gps == 'no':
            queryset = queryset.filter(
                Q(latitude__isnull=True) | Q(longitude__isnull=True)
            )
        
        # Filtre par présence de documents
        has_doc = self.request.GET.get('has_doc', '')
        if has_doc == 'yes':
            queryset = queryset.exclude(document_fourni_aex='').exclude(
                document_fourni_aex__isnull=True
            )
        elif has_doc == 'no':
            queryset = queryset.filter(
                Q(document_fourni_aex='') | Q(document_fourni_aex__isnull=True)
            )
        
        return queryset.order_by('nom')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
       
        
        context['zones'] = Zone.objects.all().order_by('numero')
        context['villes'] = Ville.objects.select_related('zone').order_by('nom')
        context['commodites'] = Commodite.objects.all().order_by('nom')
        
        # Conserver les valeurs des filtres
        context['search_params'] = {
            'nom': self.request.GET.get('nom', ''),
            'responsable': self.request.GET.get('responsable', ''),
            'zone': self.request.GET.get('zone', ''),
            'ville': self.request.GET.get('ville', ''),
            'localite': self.request.GET.get('localite', ''),
            'commodite': self.request.GET.get('commodite', ''),
            'has_gps': self.request.GET.get('has_gps', ''),
            'has_doc': self.request.GET.get('has_doc', ''),
        }
        
        context['total_results'] = self.get_queryset().count()
        
        return context