from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import JsonResponse
from django.views import View
from django.conf import settings
import requests
from fournisseurs.models import Fournisseur, FournisseurPort 
from port.models import Port
from commodites.models import Commodite, FournisseurCommodite


@login_required
def fournisseurs_map(request):
    """Vue pour afficher la carte des fournisseurs"""
    # Récupérer toutes les commodités pour les passer au template
    commodites = Commodite.objects.all()
    return render(request, 'pages/accueil.html', {'commodites': commodites})

class FournisseursAPIView(View):
    """API pour récupérer les fournisseurs en JSON avec leurs ports et commodités"""
    
    def calculate_road_distance(self, lon1, lat1, lon2, lat2):
        """Calcule la distance routière entre deux points en utilisant l'API Mapbox"""
        try:
            access_token = settings.MAPBOX_ACCESS_TOKEN
            if not access_token:
                return None
                
            # Créer les coordonnées pour l'URL de l'API
            coordinates = f"{lon1},{lat1};{lon2},{lat2}"
            url = f"https://api.mapbox.com/directions/v5/mapbox/driving/{coordinates}"
            
            # Faire la requête à l'API Mapbox
            response = requests.get(url, params={
                'access_token': access_token,
                'geometries': 'geojson',
                'overview': 'simplified',
                'steps': 'false'
            })
            
            if response.status_code == 200:
                data = response.json()
                if data.get('routes') and len(data['routes']) > 0:
                    # Retourner la distance en kilomètres, arrondie à 2 décimales
                    return round(data['routes'][0]['distance'] / 1000, 2)
        except Exception as e:
            print(f"Erreur lors du calcul de la distance routière: {e}")
        
        return None
    
    def get(self, request):
        # Précharger les relations pour optimiser les requêtes
        fournisseurs = Fournisseur.objects.select_related(
            'ville', 
            'localite'
        ).prefetch_related(
            'liens_fournisseurs__port',  # Préchargement des ports liés
            'liens_commodites__commodite'  # Préchargement des commodités liées
        ).all()
        
        data = []
        for f in fournisseurs:
            # Récupérer les ports liés avec leurs distances
            ports = []
            for lien in f.liens_fournisseurs.all():
                if lien.port and f.latitude and f.longitude and lien.port.latitude and lien.port.longitude:
                    # Calculer la distance routière avec Mapbox Directions API
                    distance_routee = self.calculate_road_distance(
                        f.longitude, f.latitude,
                        lien.port.longitude, lien.port.latitude
                    )
                    
                    ports.append({
                        'id': str(lien.port.id),
                        'nom': lien.port.nom,
                        'distance': float(lien.distance) if lien.distance else None,
                        'distance_routee': distance_routee,
                        'pays': lien.port.pays.nom if lien.port.pays else None,
                        'latitude': float(lien.port.latitude) if lien.port.latitude else None,
                        'longitude': float(lien.port.longitude) if lien.port.longitude else None
                    })
            
            # Récupérer les commodités liées
            commodites = []
            for lien in f.liens_commodites.all():
                if lien.commodite:
                    commodites.append({
                        'id': str(lien.commodite.id),
                        'nom': lien.commodite.nom,
                        'couleur': lien.commodite.couleur
                    })
            
            fournisseur_data = {
                'id': str(f.id),
                'nom': f.nom,
                'nom_responsable': f.nom_responsable,
                'latitude': float(f.latitude) if f.latitude else None,
                'longitude': float(f.longitude) if f.longitude else None,
                'contact': f.contact,
                'ville': {
                    'nom': f.ville.nom if f.ville else None
                },
                'localite': {
                    'nom': f.localite.nom if f.localite else None
                },
                'ports': ports,
                'commodites': commodites  # Liste des commodités liées
            }
            
            data.append(fournisseur_data)
        
        return JsonResponse(data, safe=False)