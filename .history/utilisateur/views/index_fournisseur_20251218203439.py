from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from fournisseurs.models import Fournisseur
from commodites.models import Commodite

from django.core.exceptions import PermissionDenied

class AccueilFournisseurView(LoginRequiredMixin, ListView):
    model = Commodite
    template_name = 'fournisseur/accueil.html'
    context_object_name = 'commodites'

    def get_queryset(self):
        user = self.request.user

        if user.type_user != 'FS':
            raise PermissionDenied("Accès réservé aux fournisseurs")

        fournisseur = getattr(user, 'fournisseur_profile', None)

        if not fournisseur:
            raise PermissionDenied("Aucun fournisseur lié à ce compte")

        return fournisseur.commodites.all()
