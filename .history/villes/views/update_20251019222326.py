from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.mixins import LoginRequiredMixin
from zones.models import Zone
from  villes.models import Ville

# ============================================================
# VUES POUR LA MODIFICATION DES VILLES
# ============================================================


class VilleUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    """
    Vue pour modifier une ville
    """
    model = Ville
    template_name = 'ville_form.html'
    fields = [
        'nom', 'zone', 'est_ville_reference', 'superficie',
        'distance_port_abidjan', 'distance_port_sanpedro', 'description'
    ]
    success_message = _("La ville %(nom)s a été modifiée avec succès")
    
    def get_success_url(self):
        return reverse_lazy('ville-detail', kwargs={'pk': self.object.pk})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _("Modifier %(nom)s") % {'nom': self.object.nom}
        context['button_text'] = _("Mettre à jour")
        return context
    
    def form_valid(self, form):
        # Vérifier si le statut de ville de référence a changé
        old_obj = Ville.objects.get(pk=self.object.pk)
        was_reference = old_obj.est_ville_reference
        
        response = super().form_valid(form)
        
        # Message supplémentaire si devient ville de référence
        if self.object.est_ville_reference and not was_reference:
            self.messages.success(
                self.request,
                _("%(nom)s est maintenant la ville de référence de la Zone %(zone)s") % {
                    'nom': self.object.nom,
                    'zone': self.object.zone.numero
                }
            )
        
        return response