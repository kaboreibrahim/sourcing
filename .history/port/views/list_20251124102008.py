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

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        context['pays_list'] = Pays.objects.all().order_by('nom')
        context['selected_pays'] = self.request.GET.get('pays', '')

        # Stat globales
        ports_qs = Port.objects.filter(deleted__isnull=True)
        context['total_ports'] = ports_qs.count()
        context['total_villes'] = (
            Ville.objects.filter(ports_villes__port__in=ports_qs, deleted__isnull=True)
            .distinct()
            .count()
        )
        context['total_localites'] = (
            Localite.objects.filter(ports_localites__port__in=ports_qs, deleted__isnull=True)
            .distinct()
            .count()
        )
        return context
