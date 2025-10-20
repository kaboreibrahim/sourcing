from django.views.generic import  DetailView
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.mixins import LoginRequiredMixin
from zones.models import Zone
 

class ZoneDetailView(LoginRequiredMixin, DetailView):
    """
    Vue pour afficher les détails d'une zone avec la liste de ses villes
    La ville de référence est affichée en tête de liste
    """
    model = Zone
    template_name = 'zone_detail.html'
    context_object_name = 'zone'
    
    def get_queryset(self):
        return Zone.objects.prefetch_related('villes')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        zone = self.object
        
        # Récupérer toutes les villes de la zone
        villes = zone.villes.filter(deleted__isnull=True)
        
        # Séparer la ville de référence et les autres villes
        ville_reference = villes.filter(est_ville_reference=True).first()
        autres_villes = villes.filter(est_ville_reference=False).order_by('nom')
        
        # Construire la liste avec la ville de référence en tête
        villes_ordonnees = []
        if ville_reference:
            villes_ordonnees.append(ville_reference)
        villes_ordonnees.extend(autres_villes)
        
        context['villes'] = villes_ordonnees
        context['ville_reference'] = ville_reference
        context['total_villes'] = villes.count()
        
        return context