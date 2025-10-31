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
# VUES POUR STATISTIQUES ET CARTOGRAPHIE
# ============================================================

class FournisseurMapView(LoginRequiredMixin, ListView):
    """
    Vue pour afficher les fournisseurs sur une carte
    """
    model = Fournisseur
    template_name = 'fournisseur_map.html'
    context_object_name = 'fournisseurs'
    
    def get_queryset(self):
        # Récupérer uniquement les fournisseurs avec coordonnées GPS
        queryset = Fournisseur.objects.select_related(
            'ville',
            'ville__zone'
        ).filter(
            latitude__isnull=False,
            longitude__isnull=False,
            deleted__isnull=True
        ).annotate(
            total_commodites=Count('liens_commodites')
        )
        
        # Filtre par zone
        zone_id = self.request.GET.get('zone', '')
        if zone_id:
            queryset = queryset.filter(ville__zone_id=zone_id)
        
        # Filtre par commodité
        commodite_id = self.request.GET.get('commodite', '')
        if commodite_id:
            queryset = queryset.filter(liens_commodites__commodite_id=commodite_id)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Préparer les données pour la carte (format JSON)
        fournisseurs_data = []
        for fournisseur in context['fournisseurs']:
            fournisseurs_data.append({
                'id': str(fournisseur.id),
                'nom': fournisseur.nom,
                'latitude': float(fournisseur.latitude),
                'longitude': float(fournisseur.longitude),
                'ville': fournisseur.ville.nom,
                'zone': fournisseur.ville.zone.numero,
                'total_commodites': fournisseur.total_commodites,
                'url': reverse_lazy('fournisseur-detail', kwargs={'pk': fournisseur.pk})
            })
        
        context['fournisseurs_json'] = fournisseurs_data
        
        
        
        context['zones'] = Zone.objects.all().order_by('numero')
        context['selected_zone'] = self.request.GET.get('zone', '')
        
        context['commodites'] = Commodite.objects.all().order_by('nom')
        context['selected_commodite'] = self.request.GET.get('commodite', '')
        
        context['total_with_coordinates'] = len(fournisseurs_data)
        context['total_fournisseurs'] = Fournisseur.objects.count()
        
        return context