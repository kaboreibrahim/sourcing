from django.views.generic import DetailView
from django.db.models import Count
from villes.models import Ville
from ..models import Pays

class PaysDetailView(DetailView):
    model = Pays
    template_name = 'pays/pays_detail.html'
    context_object_name = 'pays'
    
    def get_queryset(self):
        # Préchargement des zones et de leurs villes
        return super().get_queryset().prefetch_related(
            'zone_set__villes__localites'
        )
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pays = self.object
        
        # Statistiques
        context['nb_zones'] = pays.zone_set.count()
        
        # Récupérer les zones du pays avec leurs villes et localités
        zones = pays.zone_set.all().prefetch_related('villes__localites')
        
        # Compter le nombre total de villes à travers toutes les zones
        context['nb_villes'] = sum(zone.villes.count() for zone in zones)

        # Compter le nombre total de localités à travers toutes les villes du pays
        context['nb_localites'] = sum(
            ville.localites.count()
            for zone in zones
            for ville in zone.villes.all()
        )
        
        # Récupérer les zones avec leur nombre de villes
        zones_avec_stats = zones.annotate(
            nb_villes=Count('villes')
        ).order_by('numero')
        
        context['zones'] = zones_avec_stats

        # Liste des villes du pays (pour la section villes)
        context['villes_principales'] = (
            Ville.objects.select_related('zone', 'zone__pays')
            .filter(zone__pays=pays)
            .annotate(nb_localites=Count('localites'))
            .order_by('zone__numero', 'nom')
        )
        
        return context
