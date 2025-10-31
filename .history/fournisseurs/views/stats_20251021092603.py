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


class FournisseurStatsView(LoginRequiredMixin, ListView):
    """
    Vue pour afficher des statistiques sur les fournisseurs
    """
    model = Fournisseur
    template_name = 'fournisseur_stats.html'
    context_object_name = 'fournisseurs'
    
    def get_queryset(self):
        return Fournisseur.objects.select_related(
            'ville',
            'ville__zone'
        ).annotate(
            total_commodites=Count(
                'liens_commodites',
                filter=Q(liens_commodites__deleted__isnull=True)
            )
        ).order_by('-total_commodites', 'nom')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Statistiques générales
        context['total_fournisseurs'] = Fournisseur.objects.count()
        context['total_with_coordinates'] = Fournisseur.objects.filter(
            latitude__isnull=False,
            longitude__isnull=False
        ).count()
        context['total_with_documents'] = Fournisseur.objects.exclude(
            document_fourni_aex=''
        ).exclude(
            document_fourni_aex__isnull=True
        ).count()
        
         
        
        context['total_zones'] = Zone.objects.count()
        context['total_villes'] = Ville.objects.count()
        context['total_commodites'] = Commodite.objects.count()
        context['total_liaisons'] = FournisseurCommodite.objects.filter(
            deleted__isnull=True
        ).count()
        
        # Fournisseur avec le plus de commodités
        top_fournisseur = Fournisseur.objects.annotate(
            nb_commodites=Count('liens_commodites')
        ).order_by('-nb_commodites').first()
        
        context['top_fournisseur'] = top_fournisseur
        
        # Statistiques par zone
        from django.db.models import Count as CountFunc
        zones_data = Zone.objects.annotate(
            nb_fournisseurs=CountFunc('villes__fournisseurs', distinct=True),
            nb_commodites=CountFunc(
                'villes__fournisseurs__liens_commodites__commodite',
                distinct=True
            )
        ).order_by('numero')
        
        context['zones_data'] = zones_data
        
        # Répartition par ville (top 10)
        villes_data = Ville.objects.annotate(
            nb_fournisseurs=CountFunc('fournisseurs')
        ).filter(
            nb_fournisseurs__gt=0
        ).order_by('-nb_fournisseurs')[:10]
        
        context['villes_data'] = villes_data
        
        return context