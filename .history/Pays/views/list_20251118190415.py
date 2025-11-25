from django.views.generic import ListView
from django.db.models import Count
from ..models import Pays
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
            
        # Annotation avec le nombre de zones
        queryset = queryset.annotate(nb_zones=Count('zones', distinct=True))
        
        # Tri par défaut par nom
        return queryset.order_by('nom')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('q', '')
        return context
