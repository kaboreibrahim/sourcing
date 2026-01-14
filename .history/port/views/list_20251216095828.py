from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q, Count

from port.models import Port
from villes.models import Ville, Localite, VillePort, PortLocalite
from zones.models import Zone
from Pays.models import Pays


class PortListView(LoginRequiredMixin, ListView):
    model = Port
    template_name = 'port/port_list.html'
    context_object_name = 'ports'
    paginate_by = 20

    def get_queryset(self):
        queryset = (
            Port.objects.filter(deleted__isnull=True)
            .select_related('pays')
            .annotate(
                nb_villes=Count('ville_ports__ville', distinct=True),
                nb_localites=Count('localite_ports__localite', distinct=True),
            )
            .order_by('nom')
        )

        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(nom__icontains=search_query)
            )

        pays_id = self.request.GET.get('pays', '')
        if pays_id:
            queryset = queryset.filter(pays_id=pays_id)

        zone_id = self.request.GET.get('zone', '')
        if zone_id:
            # Ports ayant au moins une ville liée dans cette zone
            queryset = queryset.filter(ville_ports__ville__zone_id=zone_id).distinct()

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        context['selected_pays'] = self.request.GET.get('pays', '')
        context['selected_zone'] = self.request.GET.get('zone', '')
        
        # Récupérer la liste des pays
        context['pays_list'] = Pays.objects.all()
        
        # Filtrer les zones en fonction du pays sélectionné
        zones = Zone.objects.all()
        if context['selected_pays']:
            zones = zones.filter(pays_id=context['selected_pays'])
        context['zones'] = zones
        
        # Ajouter les totaux pour les statistiques
        context['total_ports'] = Port.objects.filter(deleted__isnull=True).count()
        context['total_villes'] = Port.objects.filter(
            deleted__isnull=True,
            ville_ports__isnull=False
        ).distinct().count()
        context['total_localites'] = Port.objects.filter(
            deleted__isnull=True,
            localite_ports__isnull=False
        ).distinct().count()
        
        return context


from django.http import JsonResponse
from django.views import View
from zones.models import Zone

class ZoneListAPI(View):
    def get(self, request):
        pays_id = request.GET.get('pays_id')
        zones = Zone.objects.all()
        
        if pays_id:
            zones = zones.filter(pays_id=pays_id)
            
        data = [{
            'id': zone.id,
            'numero': zone.numero
        } for zone in zones]
        
        return JsonResponse(data, safe=False)