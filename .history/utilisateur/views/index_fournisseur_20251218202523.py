from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from fournisseurs.models import Fournisseur
from commodites.models import Commodite

class AccueilFournisseurView(LoginRequiredMixin, ListView):
    model = Commodite
    template_name = 'fournisseur/accueil.html'
    context_object_name = 'commodites'
    def get_queryset(self):
        # Récupérer le fournisseur connecté
        fournisseur = self.request.user
        # Récupérer les commodités liées à ce fournisseur avec les détails
        return fournisseur.commodites.all().select_related('commodite')