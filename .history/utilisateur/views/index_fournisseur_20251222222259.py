from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from commodites.models import Commodite, FournisseurCommodite
from echantillonnages.models import Echantionnage
from django.core.exceptions import PermissionDenied
from django.db.models import Prefetch, Sum, Count, F, FloatField
from django.db.models.functions import Coalesce

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

        # Précharger les données nécessaires
        return (
            Commodite.objects
            .filter(liens_fournisseurs__fournisseur=fournisseur)
            .prefetch_related(
                Prefetch(
                    'echantillonnages',
                    queryset=Echantionnage.objects
                        .filter(fournisseur=fournisseur)
                        .order_by('-date_creation')
                )
            )
            .annotate(
                quantite_totale=Coalesce(Sum('liens_fournisseurs__quantite'), 0, output_field=FloatField()),
                prix_moyen=Coalesce(
                    Sum('liens_fournisseurs__prix_unitaire') / Count('liens_fournisseurs'),
                    0,
                    output_field=FloatField()
                )
            )
            .distinct()
        )