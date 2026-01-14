from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import JsonResponse
from django.views import View
from fournisseurs.models import Fournisseur, FournisseurPort
from port.models import Port


@login_required
def fournisseurs_map(request):
    """Vue pour afficher la carte des fournisseurs"""
    return render(request, 'pages/accueil.html')

class FournisseursAPIView(View):
    """API pour récupérer les fournisseurs en JSON"""
    
    def get(self, request):
        # Précharger les relations pour optimiser les requêtes
        fournisseurs = Fournisseur.objects.select_related(
            'ville', 
            'localite'
        ).prefetch_related(
            'liens_fournisseurs__port'  # Préchargement des ports liés
        ).all()
        
        data = []
        for f in fournisseurs:
            # Récupérer les ports liés avec leurs distances
            ports = []
            for lien in f.liens_fournisseurs.all():
                if lien.port:
                    ports.append({
                        'id': str(lien.port.id),
                        'nom': lien.port.nom,
                        'distance': float(lien.distance) if lien.distance else None,
                        'pays': lien.port.pays.nom if lien.port.pays else None,
                        'latitude': float(lien.port.latitude) if lien.port.latitude else None,
                        'longitude': float(lien.port.longitude) if lien.port.longitude else None
                    })
            
            data.append({
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
                'ports': ports  # Liste des ports liés
            })
        
        return JsonResponse(data, safe=False)