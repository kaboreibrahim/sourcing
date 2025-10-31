from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.db.models import Count, Q, Prefetch
from django.contrib.auth.mixins import LoginRequiredMixin
from fournisseurs.models import Fournisseur
from commodites.models import FournisseurCommodite, Commodite
from fournisseurs.models import Fournisseur
from zones.models import Zone
from villes.models import Ville

# ============================================================
# VUES POUR  DETAIL FOURNISSEUR
# ============================================================
 

class FournisseurDetailView(LoginRequiredMixin, DetailView):
    """
    Vue pour afficher les détails d'un fournisseur avec ses commodités
    """
    model = Fournisseur
    template_name = 'fournisseur_detail.html'
    context_object_name = 'fournisseur'
    
    def get_queryset(self):
        return Fournisseur.objects.select_related(
            'ville',
            'ville__zone'
        ).prefetch_related(
            'liens_commodites',
            'liens_commodites__commodite'
        )
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        fournisseur = self.object
        
        # Récupérer toutes les commodités fournies
        liens = fournisseur.liens_commodites.filter(
            deleted__isnull=True
        ).select_related('commodite').order_by('commodite__nom')
        
        context['liens_commodites'] = liens
        context['total_commodites'] = liens.count()
        
        # Vérifier si le fournisseur a des coordonnées GPS
        context['has_coordinates'] = fournisseur.latitude and fournisseur.longitude
        
        return context
