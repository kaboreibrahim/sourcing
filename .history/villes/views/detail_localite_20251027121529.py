from django.views.generic import  DetailView
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.mixins import LoginRequiredMixin
from zones.models import Zone
from  villes.models import Ville

# ============================================================
# VUES POUR LES DETAILS DES VILLES
# ============================================================
class VilleDetailView(LoginRequiredMixin, DetailView):
    """
    Vue pour afficher les détails d'une ville
    """
    model = Ville
    template_name = 'ville/ville_detail.html'
    context_object_name = 'ville'
    
    def get_queryset(self):
        return Ville.objects.select_related('zone')