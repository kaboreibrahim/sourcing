from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from commodites.models import Commodite
from fournisseurs.models import FournisseurCommodite
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
            return Commodite.objects.none()

        return (
            Commodite.objects
            .filter(liens_fournisseurs__fournisseur=fournisseur)
            .distinct()
        )
