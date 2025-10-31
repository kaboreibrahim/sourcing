from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.db.models import Count
from django.core.serializers.json import DjangoJSONEncoder
import json
from fournisseurs.models import Fournisseur
from commodites.models import Commodite
from zones.models import Zone


class FournisseurMapView(LoginRequiredMixin, ListView):
    """
    Vue pour afficher les fournisseurs sur une carte interactive
    avec filtres par zone et commodité
    """
    model = Fournisseur
    template_name = 'fournisseur_map.html'
    context_object_name = 'fournisseurs'
    
    def get_queryset(self):
        """
        Récupère les fournisseurs avec coordonnées GPS valides
        et applique les filtres demandés
        """
        queryset = Fournisseur.objects.select_related(
            'ville',
            'ville__zone'
        ).filter(
            latitude__isnull=False,
            longitude__isnull=False,
            deleted__isnull=True
        ).annotate(
            total_commodites=Count('liens_commodites', distinct=True)
        )
        
        # Filtre par zone
        zone_id = self.request.GET.get('zone', '').strip()
        if zone_id:
            try:
                queryset = queryset.filter(ville__zone_id=int(zone_id))
            except (ValueError, TypeError):
                pass
        
        # Filtre par commodité
        commodite_id = self.request.GET.get('commodite', '').strip()
        if commodite_id:
            try:
                queryset = queryset.filter(
                    liens_commodites__commodite_id=int(commodite_id)
                ).distinct()
            except (ValueError, TypeError):
                pass
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Préparer les données pour la carte (format JSON)
        fournisseurs_data = []
        for fournisseur in context['fournisseurs']:
            try:
                data = {
                    'id': str(fournisseur.id),
                    'nom': fournisseur.nom,
                    'latitude': float(fournisseur.latitude),
                    'longitude': float(fournisseur.longitude),
                    'ville': fournisseur.ville.nom if fournisseur.ville else '',
                    'zone': fournisseur.ville.zone.numero if fournisseur.ville and fournisseur.ville.zone else '',
                    'total_commodites': fournisseur.total_commodites,
                    'url': str(reverse_lazy('fournisseur-detail', kwargs={'pk': fournisseur.pk}))
                }
                fournisseurs_data.append(data)
            except (AttributeError, ValueError, TypeError) as e:
                # Logger l'erreur si nécessaire
                continue
        
        # Sérialiser en JSON de manière sécurisée
        context['fournisseurs_json'] = json.dumps(
            fournisseurs_data, 
            cls=DjangoJSONEncoder
        )
        
        # Données pour les filtres
        context['zones'] = Zone.objects.all().order_by('numero')
        context['selected_zone'] = self.request.GET.get('zone', '')
        
        context['commodites'] = Commodite.objects.all().order_by('nom')
        context['selected_commodite'] = self.request.GET.get('commodite', '')
        
        # Statistiques
        context['total_with_coordinates'] = len(fournisseurs_data)
        context['total_fournisseurs'] = Fournisseur.objects.filter(
            deleted__isnull=True
        ).count()
        context['total_without_coordinates'] = (
            context['total_fournisseurs'] - context['total_with_coordinates']
        )
        
        # Clé API Yandex Maps
        context['yandex_api_key'] = '09756456-236c-496a-be06-9eeb034b1845'
        
        return context