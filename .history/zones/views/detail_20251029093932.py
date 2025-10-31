from django.views.generic import DetailView
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _, ngettext
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Prefetch
from zones.models import Zone
from villes.models import Localite,Ville
from fournisseurs.models import Fournisseur
from commodites.models import Commodite, FournisseurCommodite


class ZoneDetailView(LoginRequiredMixin, DetailView):
    """
    Vue pour afficher les détails d'une zone avec la liste de ses villes,
    localités, fournisseurs et commodités associés.
    La ville de référence est affichée en tête de liste.
    """
    model = Zone
    template_name = 'zone_detail.html'
    context_object_name = 'zone'
        
    def get_queryset(self):
        # Préchargement des relations pour optimiser les requêtes
        return Zone.objects.prefetch_related(
            Prefetch(
                'villes',
                queryset=Ville.objects.filter(deleted__isnull=True)
                    .select_related('zone')
                    .prefetch_related(
                        Prefetch(
                            'localite_set',  # Utilisation du related_name par défaut
                            queryset=Localite.objects.filter(deleted__isnull=True)
                        )
                    )
                    .annotate(num_localites=Count('Localite', distinct=True))
                    .annotate(num_fournisseurs=Count('localite__fournisseurs', distinct=True))
            ),
            'villes__localite_set__fournisseurs',
            'villes__localite_set__fournisseurs__liens_commodites__commodite',
        )
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        zone = self.object
        
        # Récupérer toutes les villes de la zone avec leurs relations
        villes = zone.villes.filter(deleted__isnull=True).select_related('zone')
        
        # Séparer la ville de référence et les autres villes
        ville_reference = villes.filter(est_ville_reference=True).first()
        autres_villes = villes.filter(est_ville_reference=False).order_by('nom')
        
        # Récupérer les IDs des villes pour les requêtes suivantes
        villes_ids = list(villes.values_list('id', flat=True))
        
        # Compter les localités et fournisseurs par ville
        stats_localites = Localite.objects.filter(
            ville_id__in=villes_ids,
            deleted__isnull=True
        ).values('ville_id').annotate(
            total=Count('id')
        )
        
        stats_fournisseurs = Fournisseur.objects.filter(
            localite__ville_id__in=villes_ids,
            deleted__isnull=True
        ).values('localite__ville_id').annotate(
            total=Count('id', distinct=True)
        )
        
        # Créer des dictionnaires pour un accès rapide aux statistiques
        localites_par_ville = {stat['ville_id']: stat['total'] for stat in stats_localites}
        fournisseurs_par_ville = {stat['localite__ville_id']: stat['total'] for stat in stats_fournisseurs}
        
        # Préparer les données des villes avec leurs statistiques
        villes_avec_stats = []
        for ville in villes:
            villes_avec_stats.append({
                'id': ville.id,
                'nom': ville.nom,
                'est_ville_reference': ville.est_ville_reference,
                'description': ville.description,
                'num_localites': localites_par_ville.get(ville.id, 0),
                'num_fournisseurs': fournisseurs_par_ville.get(ville.id, 0),
                'commodites': list(Commodite.objects.filter(
                    liens_fournisseurs__fournisseur__localite__ville=ville,
                    deleted__isnull=True
                ).distinct().values_list('nom', flat=True))
            })
        
        # Construire la liste avec la ville de référence en tête
        villes_ordonnees = []
        if ville_reference:
            ref_data = next((v for v in villes_avec_stats if v['id'] == ville_reference.id), None)
            if ref_data:
                villes_ordonnees.append(ref_data)
        
        # Ajouter les autres villes
        for ville in autres_villes:
            ville_data = next((v for v in villes_avec_stats if v['id'] == ville.id), None)
            if ville_data:
                villes_ordonnees.append(ville_data)
        
        # Statistiques globales pour la zone
        total_localites = sum(localites_par_ville.values())
        total_fournisseurs = sum(fournisseurs_par_ville.values())
        
        # Récupérer toutes les commodités uniques de la zone
        commodites_zone = list(Commodite.objects.filter(
            liens_fournisseurs__fournisseur__localite__ville__in=villes_ids,
            deleted__isnull=True
        ).distinct().values_list('nom', flat=True))
        
        # Ajouter les données au contexte
        context.update({
            'villes': villes_ordonnees,
            'ville_reference': ville_reference,
            'total_villes': len(villes_ordonnees),
            'total_localites': total_localites,
            'total_fournisseurs': total_fournisseurs,
            'commodites_zone': commodites_zone,
            'has_data': len(villes_ordonnees) > 0
        })
        
        return context