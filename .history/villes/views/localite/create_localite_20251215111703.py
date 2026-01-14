
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView
from villes.models import Localite, PortLocalite
from port.models import Port
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
        # Sauvegarder d'abord la localité
        response = super().form_valid(form)
        
        # Récupérer le pays de la ville de la localité
        ville = self.object.ville
        zone = ville.zone
        pays = zone.pays
        
        # Récupérer tous les ports du même pays
        ports_du_pays = Port.objects.filter(pays=pays)
        
        # Créer des liens PortLocalite pour chaque port du pays
        for port in ports_du_pays:
            # Vérifier si le lien existe déjà avant de créer
            if not PortLocalite.objects.filter(localite=self.object, port=port).exists():
                port_localite = PortLocalite(
                    localite=self.object,
                    port=port,
                    distance=None  # La distance sera calculée plus tard si nécessaire
                )
                port_localite.save()
        
        # Message de confirmation
        messages.success(
            self.request,
            _(f"La localité {self.object.nom} a été créée et liée à {ports_du_pays.count()} port(s) du {pays.nom}.")
        )
        
        return response
 