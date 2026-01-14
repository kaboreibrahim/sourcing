from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from django.utils import timezone
from datetime import timedelta
from commodites.models import Commodite, FournisseurCommodite
from echantillonnages.models import Echantionnage
from django.core.exceptions import PermissionDenied
from django.db.models import Prefetch, Sum, Count, F, FloatField, Q
from django.db.models.functions import Coalesce, TruncMonth, ExtractWeek, ExtractYear, ExtractMonth

class AccueilFournisseurView(LoginRequiredMixin, ListView):
    model = Commodite
    template_name = 'echantillons/accueil.html'
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
                        .select_related('utilisateur')
                ),
                'liens_fournisseurs'
            )
            .distinct()
        )

        # Périodes pour les statistiques
        aujourd_hui = timezone.now().date()
        debut_mois = aujourd_hui.replace(day=1)
        debut_annee = aujourd_hui.replace(month=1, day=1)
        il_y_a_30j = aujourd_hui - timedelta(days=30)

        # Ajouter les annotations manuellement
        for commodite in commodites:
            liens = list(commodite.liens_fournisseurs.filter(fournisseur=fournisseur))
            echantillons = list(commodite.echantillonnages.all())
            
            # Calculer la quantité totale et le prix moyen
            quantite_totale = 0
            prix_unitaire = []
            
            for lf in liens:
                if hasattr(lf, 'quantite_disponible') and lf.quantite_disponible is not None:
                    quantite_totale += float(lf.quantite_disponible)
                if hasattr(lf, 'prix_unitaire') and lf.prix_unitaire is not None:
                    prix_unitaire.append(float(lf.prix_unitaire))
            
            prix_moyen = sum(prix_unitaire) / len(prix_unitaire) if prix_unitaire else 0
            
            # Statistiques des échantillons
            echantillons_mois = [e for e in echantillons if e.date_creation.date() >= debut_mois]
            echantillons_30j = [e for e in echantillons if e.date_creation.date() >= il_y_a_30j]
            
            # Dernier échantillon
            dernier_echantillon = echantillons[0] if echantillons else None
            
            # Ajouter les attributs dynamiques
            commodite.quantite_totale = quantite_totale
            commodite.prix_moyen = prix_moyen
            commodite.nb_echantillons = len(echantillons)
            commodite.nb_echantillons_mois = len(echantillons_mois)
            commodite.nb_echantillons_30j = len(echantillons_30j)
            commodite.dernier_echantillon = dernier_echantillon
            commodite.dernier_echantillon_date = dernier_echantillon.date_creation if dernier_echantillon else None
            commodite.dernier_echantillon_utilisateur = dernier_echantillon.utilisateur.get_full_name() if dernier_echantillon and hasattr(dernier_echantillon, 'utilisateur') else 'Inconnu'

        return commodites
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        fournisseur = getattr(user, 'fournisseur_profile', None)
        
        if fournisseur:
            # Statistiques globales
            echantillons = Echantionnage.objects.filter(fournisseur=fournisseur)
            
            # Nombre total d'échantillons
            context['total_echantillons'] = echantillons.count()
            
            # Nombre d'échantillons ce mois-ci
            debut_mois = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            context['echantillons_mois'] = echantillons.filter(date_creation__gte=debut_mois).count()
            
            # Derniers échantillons (pour le tableau de bord)
            context['derniers_echantillons'] = echantillons.select_related('commodite', 'utilisateur')[:5]
            
            # Statistiques par mois pour le graphique
            stats_mensuelles = echantillons.annotate(
                mois=TruncMonth('date_creation'),
                annee=ExtractYear('date_creation'),
                semaine=ExtractWeek('date_creation')
            ).values('mois').annotate(
                total=Count('id'),
                annee=ExtractYear('mois'),
                mois=ExtractMonth('mois')
            ).order_by('mois')
            
            context['stats_mensuelles'] = list(stats_mensuelles)
            
        return context