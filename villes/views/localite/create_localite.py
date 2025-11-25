
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView
from  villes.models import Localite
from django.conf import settings
from django.contrib import messages
# ============================================================
# VUES POUR LA CREATION DE localite 
# ============================================================
class LocaliteCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    """
    Vue pour créer une nouvelle localite
    """
    model = Localite
    template_name = 'localite/localite_form.html'
    fields = [
        'nom', 'ville',
        'latitude', 'longitude','superficie'  
    ]
    success_message = _("La localite %(nom)s a été créée avec succès")
    
    def get_success_url(self):
        return reverse_lazy('localite-detail', kwargs={'pk': self.object.pk})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _("Créer une nouvelle localite")
        context['button_text'] = _("Créer")

        # Ajouter le token Mapbox pour la carte interactive
        context['mapbox_token'] = getattr(settings, 'MAPBOX_ACCESS_TOKEN', '')
        
        # Si une ville est passée en paramètre
        ville_id = self.request.GET.get('ville')
        if ville_id:
            context['ville_preselected'] = ville_id
        
        return context
    
    def form_valid(self, form):
        response = super().form_valid(form)
        
        messages.success(self.request, _("La localite %(nom)s a été créée avec succès") % {'nom': self.object.nom})
        return response
 