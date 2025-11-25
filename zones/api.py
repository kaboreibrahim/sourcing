from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
import json

from zones.models import Zone

@csrf_exempt
@require_http_methods(["GET"])
def zones_by_pays(request, pays_id):
    """
    Vue API pour récupérer les zones d'un pays donné
    """
    try:
        # Récupérer les zones du pays
        zones = Zone.objects.filter(pays_id=pays_id).values('id', 'numero', 'nom')
        
        # Convertir le QuerySet en liste de dictionnaires
        zones_list = list(zones)
        
        return JsonResponse({
            'status': 'success',
            'data': zones_list
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)
