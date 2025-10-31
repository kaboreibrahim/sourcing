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


class FournisseurUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    """
    Vue pour modifier un fournisseur
    """
    model = Fournisseur
    template_name = 'fournisseur_form.html'
    fields = [
        'nom', 'nom_responsable', 'contact', 'ville', 'localite',
        'latitude', 'longitude', 'distance_port_abidjan', 
        'distance_port_sanpedro', 'document_fourni_aex'
    ]
    success_message = _("Le fournisseur %(nom)s a été modifié avec succès")
    
    def get_success_url(self):
        return reverse_lazy('fournisseur-detail', kwargs={'pk': self.object.pk})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _("Modifier %(nom)s") % {'nom': self.object.nom}
        context['button_text'] = _("Mettre à jour")
        return context
