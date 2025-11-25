# port/views.py
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .models import Port

@require_http_methods(["GET"])
def get_ports_by_pays(request, pays_id):
    try:
        ports = Port.objects.filter(pays_id=pays_id, deleted__isnull=True)
        ports_data = [{'id': port.id, 'nom': port.nom} for port in ports]
        return JsonResponse({'ports': ports_data})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)