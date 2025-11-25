from django.views.generic import ListView
from django.db.models import Count, Prefetch
from villes.models import Ville, Localite
from zones.models import Zone
from Pays.models import Pays
from django.db.models import Q


class PaysListView(ListView):
    model = Pays
    template_name = 'pays/pays_list.html'
    context_object_name = 'pays_list'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtrage par recherche
        search_query = self.request.GET.get('q')
        if search_query:
            queryset = queryset.filter(
                Q(nom__icontains=search_query) |
                Q(code__iexact=search_query)
            )
        
        # Préchargement des relations avec limite pour l'aperçu
        queryset = queryset.prefetch_related(
            Prefetch(
                'zone_set',
                queryset=Zone.objects.all()[:3],
                to_attr='zones_preview'
            ),
            Prefetch(
                'zone_set__villes',
                queryset=Ville.objects.select_related('zone')[:3],
                to_attr='villes_preview'
            ),
            Prefetch(
                'zone_set__villes__localites',
                queryset=Localite.objects.select_related('ville')[:3],
                to_attr='localites_preview'
            )
        )
        
        # Annotations avec les comptes corrects
        queryset = queryset.annotate(
            nb_zones=Count('zone_set', distinct=True),
            nb_villes=Count('zone_set__villes', distinct=True),
            nb_localites=Count('zone_set__villes__localites', distinct=True)
        )
        
        # Tri par défaut par nom
        return queryset.order_by('nom')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('q', '')
        return context