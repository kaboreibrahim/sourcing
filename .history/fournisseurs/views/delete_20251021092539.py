from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.db.models import Count, Q, Prefetch
from django.contrib.auth.mixins import LoginRequiredMixin
from fournisseurs.models import Fournisseur
from commodites.models import FournisseurCommodite, Commodite
from zones.models import Zone
from villes.models import Ville
class FournisseurDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    """
    Vue pour supprimer un fournisseur (suppression logique avec safedelete)
    """
    model = Fournisseur
    template_name = 'fournisseur_confirm_delete.html'
    success_url = reverse_lazy('fournisseur-list')
    success_message = _("Le fournisseur a été supprimé avec succès")
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_commodites'] = self.object.liens_commodites.filter(
            deleted__isnull=True
        ).count()
        return context
