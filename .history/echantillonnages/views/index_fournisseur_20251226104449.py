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

        # Récupérer d'abord les commodités liées au fournisseur
        commodites = (
            Commodite.objects
            .filter(liens_fournisseurs__fournisseur=fournisseur)
            .prefetch_related(
                Prefetch(
                    'echantillonnages',
                    queryset=Echantionnage.objects
                        .filter(fournisseur=fournisseur)
                        .order_by('-date_creation')
                ),
                'liens_fournisseurs'
            )
            .distinct()
        )

        # Ajouter les annotations manuellement
        for commodite in commodites:
            # Calculer la quantité totale
            quantite_totale = sum(
                float(lf.quantite_disponible) 
                for lf in commodite.liens_fournisseurs.all() 
                if hasattr(lf, 'quantite_disponible') and lf.quantite_disponible is not None
            )
            
            # Calculer le prix moyen
            prix_unitaire = [
                float(lf.prix_unitaire) 
                for lf in commodite.liens_fournisseurs.all() 
                if hasattr(lf, 'prix_unitaire') and lf.prix_unitaire is not None
            ]
            prix_moyen = sum(prix_unitaire) / len(prix_unitaire) if prix_unitaire else 0

            # Ajouter les attributs dynamiques
            commodite.quantite_totale = quantite_totale
            commodite.prix_moyen = prix_moyen

        return commodites