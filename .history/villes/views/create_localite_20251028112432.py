# from django.views.generic import   CreateView
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.mixins import LoginRequiredMixin
from zones.models import Zone
from  villes.models import Ville

# ============================================================
# VUES POUR LA CREATION DE localite 
# ============================================================
class localiteCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    """
    Vue pour créer une nouvelle ville
    """
    model = Ville
    template_name = 'ville_form.html'
    fields = [
        'nom', 'zone', 'est_ville_reference', 'superficie',
        'distance_port_abidjan', 'distance_port_sanpedro', 'description'
    ]
    success_message = _("La ville %(nom)s a été créée avec succès")
    
    def get_success_url(self):
        return reverse_lazy('ville-detail', kwargs={'pk': self.object.pk})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _("Créer une nouvelle ville")
        context['button_text'] = _("Créer")
        
        # Si une zone est passée en paramètre
        zone_id = self.request.GET.get('zone')
        if zone_id:
            context['zone_preselected'] = zone_id
        
        return context
    
    def form_valid(self, form):
        response = super().form_valid(form)
        
        # Message supplémentaire si c'est une ville de référence
        if self.object.est_ville_reference:
            self.messages.success(
                self.request,
                _("%(nom)s est maintenant la ville de référence de la Zone %(zone)s") % {
                    'nom': self.object.nom,
                    'zone': self.object.zone.numero
                }
            )
        
        return response
 