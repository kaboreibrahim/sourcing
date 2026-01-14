# In utilisateur/views/index_fournisseur.py
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from commodites.models import Commodite, FournisseurCommodite
from echantillonnages.models import Echantionnage
from django.core.exceptions import PermissionDenied
from django.db.models import Prefetch

class AccueilFournisseurView(LoginRequiredMixin, ListView):
    model = Commodite
    template_name = 'fournisseur/accueil.html'
    context_object_name = 'commodites'

    def get_queryset(self):
        user = self.request.user

        if user.type_user != 'FS':
            raise PermissionDenized("Accès réservé aux fournisseurs")

        fournisseur = getattr(user, 'fournisseur_profile', None)
        if not fournisseur:
            return Commodite.objects.none()

        # Prefetch related echantillonnages for each commodite
        return (
            Commodite.objects
            .filter(liens_fournisseurs__fournisseur=fournisseur)
            .prefetch_related(
                Prefetch(
                    'echantillonnages',
                    queryset=Echantionnage.objects.filter(fournisseur=fournisseur).order_by('-date_creation')
                )
            )
            .distinct()
        )