from django.shortcuts import render
from django.contrib.auth.decorators import login_required
@login_required
def accueil (request):
    
    
    return render(request,'pages/accueil.html')


from django.shortcuts import render
from django.http import JsonResponse
from django.views import View
from fournisseurs.models import Fournisseur
@login_required
def fournisseurs_map(request):
    """Vue pour afficher la carte des fournisseurs"""
    return render(request, 'fournisseurs/map.html')

class FournisseursAPIView(View):
    """API pour récupérer les fournisseurs en JSON"""
    
    def get(self, request):
        fournisseurs = Fournisseur.objects.select_related('ville', 'localite').all()
        
        data = []
        for f in fournisseurs:
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
                'distance_port_abidjan': float(f.distance_port_abidjan) if f.distance_port_abidjan else None,
                'distance_port_sanpedro': float(f.distance_port_sanpedro) if f.distance_port_sanpedro else None,
            })
        
        return JsonResponse(data, safe=False)