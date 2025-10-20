from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.mixins import LoginRequiredMixin
from zones.models import Zone


class ZoneDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    """
    Vue pour supprimer une zone (suppression logique avec safedelete)
    """
    model = Zone
    template_name = 'zone_confirm_delete.html'
    success_url = reverse_lazy('zone-list')
    success_message = _("La zone a été supprimée avec succès")
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_villes'] = self.object.villes.count()
        return context

