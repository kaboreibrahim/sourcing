# from django.views.generic import   CreateView
# from django.contrib.messages.views import SuccessMessageMixin
# from django.urls import reverse_lazy
# from django.utils.translation import gettext_lazy as _
# from django.contrib.auth.mixins import LoginRequiredMixin
# from zones.models import Zone
# from  villes.models import Ville

# # ============================================================
# # VUES POUR LA CREATION DES VILLES
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
from django.contrib.auth.mixins import LoginRequiredMixin
from zones.models import Zone
from villes.models import Ville

# ============================================================
# VUES POUR LA CREATION DES VILLES
# ============================================================
class VilleCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    """
    Vue pour créer une nouvelle ville avec intégration Yandex Maps
    """
    model = Ville
    template_name = 'ville_form.html'
    fields = [
        'nom', 'zone', 'est_ville_reference', 'superficie',
        'distance_port_abidjan', 'distance_port_sanpedro', 'description'
    ]
    success_message = _("La ville %(nom)s a été créée avec succès")
   
    def get_success_url(self):
        return reverse_lazy('ville-detail', kwargs={'pk': self.object.pk})
   
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _("Créer une nouvelle ville")
        context['button_text'] = _("Créer")
        
        # Clé API Yandex Maps
        context['yandex_api_key'] = '09756456-236c-496a-be06-9eeb034b1845'
        
        # Coordonnées des ports (Côte d'Ivoire)
        context['port_abidjan'] = {
            'lat':5.2239587,
            'lon': -3.8230705,
            'nom': 'Port Autonome d\'Abidjan'
        }
        context['port_sanpedro'] = {
            'lat': -6.619978,
            'lon':4.739742,
            'nom': 'Port de San-Pédro'
        }
       
        # Si une zone est passée en paramètre
        zone_id = self.request.GET.get('zone')
        if zone_id:
            context['zone_preselected'] = zone_id
       
        return context
   
    def form_valid(self, form):
        response = super().form_valid(form)
       
        # Message supplémentaire si c'est une ville de référence
        if self.object.est_ville_reference:
            self.messages.success(
                self.request,
                _("%(nom)s est maintenant la ville de référence de la Zone %(zone)s") % {
                    'nom': self.object.nom,
                    'zone': self.object.zone.numero
                }
            )
       
        return response