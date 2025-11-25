from django.views.generic import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count

from port.models import Port
from villes.models import VillePort, PortLocalite


class PortDetailView(LoginRequiredMixin, DetailView):
    model = Port
    template_name = 'port/port_detail.html'
    context_object_name = 'port'

    def get_queryset(self):
        return Port.objects.select_related('pays').filter(deleted__isnull=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        port = self.object

        # Liaisons avec les villes
        liaisons_villes = (
            VillePort.objects.select_related('ville', 'ville__zone', 'ville__zone__pays')
            .filter(port=port, deleted__isnull=True)
        )

        # Liaisons avec les localités
        liaisons_localites = (
            PortLocalite.objects.select_related('localite', 'localite__ville', 'localite__ville__zone')
            .filter(port=port, deleted__isnull=True)
        )

        villes = [lp.ville for lp in liaisons_villes]
        zones = {v.zone for v in villes}
        localites = [pl.localite for pl in liaisons_localites]

        context.update({
            'liaisons_villes': liaisons_villes,
            'liaisons_localites': liaisons_localites,
            'villes_associees': villes,
            'zones_associees': zones,
            'localites_associees': localites,
            'nb_villes': len({v.id for v in villes}),
            'nb_zones': len({z.id for z in zones}),
            'nb_localites': len({l.id for l in localites}),
        })
        return context
