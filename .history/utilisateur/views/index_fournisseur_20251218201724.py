from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from fournisseurs.models import Fournisseur
from commodites.models import Commodite

class AccueilFournisseurView(LoginRequiredMixin, ListView):
    template_name = 'fournisseur/accueil.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Ajoutez ici les données que vous voulez passer au template
        context['titre'] = 'Bienvenue sur Sourcing'
        context['sous_titre'] = 'Votre plateforme de gestion des fournisseurs'
        return context