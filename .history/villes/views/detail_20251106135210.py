from django.views.generic import DetailView
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.mixins import LoginRequiredMixin
from zones.models import Zone
from villes.models import Ville, Localite

# ============================================================
# VUES POUR LES DETAILS DES VILLES
# ============================================================
class VilleDetailView(LoginRequiredMixin, DetailView):
    """
    Vue pour afficher les détails d'une ville avec ses localités
    """
    model = Ville
    template_name = 'ville/ville_detail.html'
    context_object_name = 'ville'
    
    def get_queryset(self):
        return Ville.objects.select_related('zone').prefetch_related('localites')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Récupérer les localités de la ville
        context['localites'] = self.object.localites.all().order_by('nom')
        context['nombre_localites'] = context['localites'].count()
        return context