from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.db.models import Count, Q, Prefetch
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Commodite, FournisseurCommodite


# ============================================================
# VUES POUR COMMODITE
# ============================================================




class CommoditeCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    """
    Vue pour créer une nouvelle commodité
    """
    model = Commodite
    template_name = 'commodites/commodite_form.html'
    fields = ['nom']
    success_message = _("La commodité %(nom)s a été créée avec succès")
    
    def get_success_url(self):
        return reverse_lazy('commodite-detail', kwargs={'pk': self.object.pk})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _("Créer une nouvelle commodité")
        context['button_text'] = _("Créer")
        return context

 