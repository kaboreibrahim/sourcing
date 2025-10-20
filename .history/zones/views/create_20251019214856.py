from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.db.models import Count, Q, Prefetch
from django.contrib.auth.mixins import LoginRequiredMixin
from zones.models import Zone
from  villes.models import Ville



class ZoneCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    """
    Vue pour créer une nouvelle zone
    """
    model = Zone
    template_name = 'zone_form.html'
    fields = ['description']
    success_message = _("La zone %(numero)s a été créée avec succès")
    
    def get_success_url(self):
        return reverse_lazy('zone-detail', kwargs={'pk': self.object.pk})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _("Créer une nouvelle zone")
        context['button_text'] = _("Créer")
        return context