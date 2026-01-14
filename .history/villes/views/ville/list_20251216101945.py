from django.views.generic import ListView 
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.db.models import Q, Count
from django.views import View
from django.http import JsonResponse
from django.db.models import Prefetch

from villes.models import Ville, VillePort
from Pays.models import Pays
from zones.models import Zone 
class ZoneListAPI(View):
    def get(self, request):
        pays_id = request.GET.get('pays_id')
        zones = Zone.objects.all()
        
        if pays_id:
            zones = zones.filter(pays_id=pays_id)
            
        data = [{
            'id': str(zone.id),
            'numero': zone.numero
        } for zone in zones]
        
        return JsonResponse(data, safe=False)

class VilleListView(ListView):
    model = Ville
    template_name = 'ville/ville_list.html'
    context_object_name = 'villes'
    paginate_by = 20
        
    def get_queryset(self):
        queryset = (
            Ville.objects.select_related('zone', 'zone__pays')
            .prefetch_related(
                Prefetch(
                    'ports_villes',
                    queryset=VillePort.objects.select_related('port').order_by('port__nom')
                )
            )
            .annotate(localites_count=Count('localites', distinct=True))
            .order_by('zone__pays__nom', 'zone__numero', 'nom')
        )
        
        # Filtres
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(nom__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(zone__numero__icontains=search_query) |
                Q(zone__pays__nom__icontains=search_query)
            )

        selected_pays = self.request.GET.get('pays')
        if selected_pays:
            queryset = queryset.filter(zone__pays_id=selected_pays)

        selected_zone = self.request.GET.get('zone')
        if selected_zone:
            queryset = queryset.filter(zone_id=selected_zone)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        context['selected_pays'] = self.request.GET.get('pays', '')
        context['selected_zone'] = self.request.GET.get('zone', '')
        context['pays_list'] = Pays.objects.all().order_by('nom')
        
        # Filtrer les zones en fonction du pays sélectionné
        zones = Zone.objects.all()
        if context['selected_pays']:
            zones = zones.filter(pays_id=context['selected_pays'])
        context['zones'] = zones.order_by('numero')
        
        # Statistiques
        context['total_villes'] = Ville.objects.filter(deleted__isnull=True).count()
        
        return context