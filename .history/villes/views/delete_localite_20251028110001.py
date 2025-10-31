from django.views.generic import DeleteView
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.mixins import LoginRequiredMixin

from  villes.models import Localite


# ============================================================
# VUES POUR LA SUPPRESSION DES LOCALITES
# ============================================================
class LocaliteDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    """
    Vue pour supprimer une localite (suppression logique avec safedelete)
    """
    model = Localite
    template_name = 'localite_confirm_delete.html'
    success_url = reverse_lazy('localite-list')
    success_message = _("La localite a été supprimée avec succès")
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context