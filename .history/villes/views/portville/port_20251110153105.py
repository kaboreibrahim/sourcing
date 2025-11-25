# villes/views/portville/ports.py
from django.http import JsonResponse
from port.models import Port
from django.views.decorators.http import require_http_methods
from django.utils.translation import gettext_lazy as _

@require_http_methods(["GET"])
def get_ports_by_ville_pays(request, ville_id=None):
    try:
        if ville_id and ville_id != '0':
            from villes.models import Ville
            try:
                ville = Ville.objects.get(pk=ville_id)
                ports = Port.objects.filter(pays=ville.pays, deleted__isnull=True)
            except Ville.DoesNotExist:
                ports = Port.objects.filter(deleted__isnull=True)
        else:
            ports = Port.objects.filter(deleted__isnull=True)
            
        ports_data = [{'id': port.id, 'nom': port.nom} for port in ports]
        return JsonResponse({'ports': ports_data})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)