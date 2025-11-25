from django.views.generic import DetailView
from django.db.models import Count
from ..models import Pays

class PaysDetailView(DetailView):
    model = Pays
    template_name = 'pays/pays_detail.html'
    context_object_name = 'pays'
    
    def get_queryset(self):
        # Préchargement des zones et de leurs villes
        return super().get_queryset().prefetch_related(
            'zone_set__villes'
        )
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pays = self.object
        
        # Statistiques
        context['nb_zones'] = pays.zone_set.count()
        
        # Compter le nombre total de villes à travers toutes les zones
        zones = pays.zone_set.all().prefetch_related('villes')
        context['nb_villes'] = sum(zone.villes.count() for zone in zones)
        
        # Récupérer les zones avec leur nombre de villes
        zones_avec_stats = zones.annotate(
            nb_villes=Count('villes')
        ).order_by('numero')
        
        context['zones'] = zones_avec_stats
        
        return context
