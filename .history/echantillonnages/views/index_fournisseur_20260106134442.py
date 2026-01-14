from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from django.core.exceptions import PermissionDenied
from django.db.models import Prefetch, Avg, F, FloatField, Case, When, Value, IntegerField, Sum, Q
from django.db.models.functions import Coalesce, Round
from django.utils.translation import gettext_lazy as _

# Import des modèles
from commodites.models import Commodite, FournisseurCommodite
from echantillonnages.models import Echantionnage

class AccueilFournisseurView(LoginRequiredMixin, ListView):
    """
    Vue pour l'accueil des fournisseurs, affichant les commodités liées avec leurs statistiques.
    """
    model = Commodite
    template_name = 'echantillons/accueil.html'
    context_object_name = 'commodites'
    paginate_by = 10

    def dispatch(self, request, *args, **kwargs):
        """Vérifie que l'utilisateur est bien un fournisseur."""
        if not request.user.is_authenticated or request.user.type_user != 'FS':
            raise PermissionDenied(_("Accès réservé aux fournisseurs"))
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        """
        Récupère les commodités avec leurs statistiques pour le fournisseur connecté.
        Optimisé pour réduire le nombre de requêtes SQL.
        """
        fournisseur = getattr(self.request.user, 'fournisseur_profile', None)
        if not fournisseur:
            return Commodite.objects.none()

        # Préchargement des relations pour optimiser les performances
        prefetch_echantillonnages = Prefetch(
            'echantillonnages',
            queryset=Echantionnage.objects
                .filter(fournisseur=fournisseur)
                .order_by('-date_creation')
        )

        # Annotations pour les calculs directement en base de données
        return (
            Commodite.objects
            .filter(echantillonnages__fournisseur=fournisseur)
            .prefetch_related(
                prefetch_echantillonnages,
                Prefetch(
                    'echantillonnages',
                    queryset=Echantionnage.objects.filter(fournisseur=fournisseur)
                )
            )
            .annotate(
                quantite_totale=Coalesce(
                    Sum('echantillonnages__quantite', 
                        filter=Q(echantillonnages__fournisseur=fournisseur),
                        output_field=FloatField()
                    ),
                    Value(0.0, output_field=FloatField())
                ),
                prix_moyen=Coalesce(
                    Avg('echantillonnages__prix',
                        filter=Q(echantillonnages__fournisseur=fournisseur) & 
                               Q(echantillonnages__prix__isnull=False),
                        output_field=FloatField()
                    ),
                    Value(0.0, output_field=FloatField())
                ),
                # statut_disponibilite=Case(
                #     When(quantite_totale__gt=0, then=Value('disponible')),
                #     default=Value('indisponible'),
                #     output_field=CharField()
                # )
            )
            .distinct()
        )

    def get_context_data(self, **kwargs):
        """Ajoute des statistiques supplémentaires au contexte."""
        context = super().get_context_data(**kwargs)
        context['total_commodites'] = self.get_queryset().count()
        
        # Calcul des statistiques globales
        if context['commodites']:
            context['moyenne_prix'] = round(
                sum(c.prix_moyen for c in context['commodites'] if hasattr(c, 'prix_moyen')) / 
                len(context['commodites']), 2)
            context['quantite_totale'] = sum(
                c.quantite_totale for c in context['commodites'] 
                if hasattr(c, 'quantite_totale'))
                
        return context