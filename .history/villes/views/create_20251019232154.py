from django.views.generic import   CreateView
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.mixins import LoginRequiredMixin
from zones.models import Zone
from  villes.models import Ville

# ============================================================
# VUES POUR LA CREATION DES VILLES
# # ============================================================
# class VilleCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
#     """
#     Vue pour créer une nouvelle ville
#     """
#     model = Ville
#     template_name = 'ville_form.html'
#     fields = [
#         'nom', 'zone', 'est_ville_reference', 'superficie',
#         'distance_port_abidjan', 'distance_port_sanpedro', 'description'
#     ]
#     success_message = _("La ville %(nom)s a été créée avec succès")
    
#     def get_success_url(self):
#         return reverse_lazy('ville-detail', kwargs={'pk': self.object.pk})
    
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['title'] = _("Créer une nouvelle ville")
#         context['button_text'] = _("Créer")
        
#         # Si une zone est passée en paramètre
#         zone_id = self.request.GET.get('zone')
#         if zone_id:
#             context['zone_preselected'] = zone_id
        
#         return context
    
#     def form_valid(self, form):
#         response = super().form_valid(form)
        
#         # Message supplémentaire si c'est une ville de référence
#         if self.object.est_ville_reference:
#             self.messages.success(
#                 self.request,
#                 _("%(nom)s est maintenant la ville de référence de la Zone %(zone)s") % {
#                     'nom': self.object.nom,
#                     'zone': self.object.zone.numero
#                 }
#             )
        
#         return response


from django.views.generic import CreateView
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
from ..models import Ville

class VilleCreateView(SuccessMessageMixin, CreateView):
    model = Ville
    template_name = 'ville_form.html'
    fields = ['nom', 'zone', 'est_ville_reference', 'description', 
              'superficie', 'distance_port_abidjan', 'distance_port_sanpedro',
              'latitude', 'longitude']
    success_url = reverse_lazy('ville-list')
    success_message = _("La ville a été créée avec succès.")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _("Ajouter une nouvelle ville")
        context['yandex_maps_api_key'] = '256c2512-f04c-4d6f-832c-6f0ad8e1ecde  '  # À remplacer par votre clé API
        return context

@csrf_exempt
@require_http_methods(["POST"])
def calculate_distance(request):
    try:
        data = json.loads(request.body)
        lat1 = float(data.get('lat1'))
        lon1 = float(data.get('lon1'))
        lat2 = float(data.get('lat2'))
        lon2 = float(data.get('lon2'))
        
        # Calcul de la distance en kilomètres (formule de Haversine)
        from math import radians, sin, cos, sqrt, atan2
        R = 6371.0  # Rayon de la Terre en km
        
        lat1_rad = radians(lat1)
        lon1_rad = radians(lon1)
        lat2_rad = radians(lat2)
        lon2_rad = radians(lon2)
        
        dlon = lon2_rad - lon1_rad
        dlat = lat2_rad - lat1_rad
        
        a = sin(dlat / 2)**2 + cos(lat1_rad) * cos(lat2_rad) * sin(dlon / 2)**2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        distance = R * c
        
        return JsonResponse({'distance': round(distance, 2)})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)