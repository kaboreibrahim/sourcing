from django.views.generic import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Prefetch, Q
from django.core.cache import cache
from zones.models import Zone
from villes.models import Localite, Ville
from fournisseurs.models import Fournisseur
from commodites.models import Commodite


class ZoneDetailView(LoginRequiredMixin, DetailView):
    """
    Vue optimisée pour afficher les détails d'une zone avec interface moderne.
    Affiche les villes, fournisseurs et commodités avec chargement dynamique.
    """
    model = Zone
    template_name = 'zone_detail.html'
    context_object_name = 'zone'
    
    def get_queryset(self):
        """Préchargement optimisé des relations"""
        return Zone.objects.prefetch_related(
            Prefetch(
                'villes',
                queryset=Ville.objects.filter(deleted__isnull=True)
                    .select_related('zone')
                    .prefetch_related(
                        Prefetch(
                            'localites',
                            queryset=Localite.objects.filter(deleted__isnull=True)
                                .prefetch_related(
                                    Prefetch(
                                        'fournisseurs',
                                        queryset=Fournisseur.objects.filter(deleted__isnull=True)
                                            .prefetch_related('liens_commodites__commodite')
                                    )
                                )
                        )
                    )
            )
        )
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        zone = self.object
        
        # Tentative de récupération depuis le cache
        cache_key = f'zone_detail_{zone.id}'
        cached_data = cache.get(cache_key)
        
        if cached_data:
            context.update(cached_data)
            return context
        
        # Récupérer toutes les villes de la zone
        villes = zone.villes.filter(deleted__isnull=True)
        
        # Identifier la ville de référence
        ville_reference = villes.filter(est_ville_reference=True).first()
        
        # Préparer les données des villes avec statistiques
        villes_data = []
        total_localites = 0
        total_fournisseurs = 0
        commodites_zone_set = set()
        
        for ville in villes:
            # Compter les localités de cette ville
            localites = ville.localites.filter(deleted__isnull=True)
            num_localites = localites.count()
            
            # Compter les fournisseurs uniques de cette ville
            fournisseurs_ids = set()
            commodites_ville = set()
            
            for localite in localites:
                for fournisseur in localite.fournisseurs.filter(deleted__isnull=True):
                    fournisseurs_ids.add(fournisseur.id)
                    
                    # Récupérer les commodités de ce fournisseur
                    for lien in fournisseur.liens_commodites.filter(
                        commodite__deleted__isnull=True
                    ):
                        commodite_nom = lien.commodite.nom
                        commodites_ville.add(commodite_nom)
                        commodites_zone_set.add(commodite_nom)
            
            num_fournisseurs = len(fournisseurs_ids)
            
            # Accumuler les totaux
            total_localites += num_localites
            total_fournisseurs += num_fournisseurs
            
            # Construire les données de la ville
            ville_data = {
                'id': ville.id,
                'nom': ville.nom,
                'description': ville.description or '',
                'est_ville_reference': ville.est_ville_reference,
                'num_localites': num_localites,
                'num_fournisseurs': num_fournisseurs,
                'commodites': sorted(list(commodites_ville)),
                'updated_at': ville.updated_at
            }
            
            villes_data.append(ville_data)
        
        # Trier les villes : ville de référence en premier, puis par nom
        villes_data.sort(key=lambda v: (not v['est_ville_reference'], v['nom']))
        
        # Préparer le contexte
        context_data = {
            'villes': villes_data,
            'ville_reference': ville_reference,
            'total_villes': len(villes_data),
            'total_localites': total_localites,
            'total_fournisseurs': total_fournisseurs,
            'commodites_zone': sorted(list(commodites_zone_set)),
            'has_data': len(villes_data) > 0
        }
        
        # Mettre en cache pour 5 minutes
        cache.set(cache_key, context_data, 300)
        
        context.update(context_data)
        return context


class ZoneDetailAPIView(LoginRequiredMixin, DetailView):
    """
    Vue API JSON pour charger les détails d'une ville spécifique
    de manière asynchrone (optionnel, pour amélioration future)
    """
    model = Ville
    
    def render_to_response(self, context, **response_kwargs):
        from django.http import JsonResponse
        
        ville = self.object
        
        # Récupérer les localités avec leurs fournisseurs
        localites_data = []
        
        for localite in ville.localites.filter(deleted__isnull=True):
            fournisseurs_data = []
            
            for fournisseur in localite.fournisseurs.filter(deleted__isnull=True):
                commodites = [
                    lien.commodite.nom 
                    for lien in fournisseur.liens_commodites.filter(
                        commodite__deleted__isnull=True
                    )
                ]
                
                fournisseurs_data.append({
                    'id': fournisseur.id,
                    'nom': fournisseur.nom,
                    'type': fournisseur.type_fournisseur,
                    'contact': fournisseur.contact or '',
                    'commodites': commodites
                })
            
            localites_data.append({
                'id': localite.id,
                'nom': localite.nom,
                'description': localite.description or '',
                'fournisseurs': fournisseurs_data
            })
        
        data = {
            'id': ville.id,
            'nom': ville.nom,
            'description': ville.description or '',
            'est_reference': ville.est_ville_reference,
            'localites': localites_data
        }
        
        return JsonResponse(data)