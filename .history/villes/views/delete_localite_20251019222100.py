from django.views.generic import DeleteView
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.mixins import LoginRequiredMixin
from zones.models import Zone
from  villes.models import Ville


# ============================================================
# VUES POUR LA SUPPRESSION DES VILLES
# ============================================================
class VilleDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    """
    Vue pour supprimer une ville (suppression logique avec safedelete)
    """
    model = Ville
    template_name = 'ville_confirm_delete.html'
    success_url = reverse_lazy('ville-list')
    success_message = _("La ville a été supprimée avec succès")
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_reference'] = self.object.est_ville_reference
        return context