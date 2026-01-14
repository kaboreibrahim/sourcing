
from django.db.models import Sum, Subquery, OuterRef
from django.views.generic import TemplateView
from echantillonnages.models import Echantionnage
from commodites.models import Commodite

class AccueilView(TemplateView):
    template_name = 'website/accueil1.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Récupérer le dernier échantillon pour chaque couple (commodité, fournisseur)
        derniers_echantillons = Echantionnage.objects.filter(
            id__in=Subquery(
                Echantionnage.objects.filter(
                    commodite=OuterRef('commodite'),
                    fournisseur=OuterRef('fournisseur')
                ).order_by('-date_creation').values('id')[:1]
            )
        ).select_related('fournisseur', 'commodite')
        
        # Récupérer toutes les commodités
        commodites = Commodite.objects.all()
        
        # Préparer les données pour le template
        disponibilites = []
        total_general = 0  # Variable pour la somme totale
        
        for commodite in commodites:
            # Filtrer les échantillons pour la commodité courante
            echantillons_commodite = derniers_echantillons.filter(commodite=commodite)
            
            # Calculer la quantité totale pour la commodité (somme des quantités des derniers échantillons)
            quantite_totale = sum(e.quantite for e in echantillons_commodite)
            total_general += quantite_totale  # Ajouter au total général
            
            # Préparer la liste des fournisseurs avec leur dernière quantité
            fournisseurs_data = []
            for echantillon in echantillons_commodite.order_by('-quantite')[:3]:  # Prendre les 3 plus gros fournisseurs
                fournisseurs_data.append({
                    'id': str(echantillon.fournisseur.id),
                    'nom': echantillon.fournisseur.nom,
                    'quantite': echantillon.quantite,
                    'date': echantillon.date_creation
                })
            
            if fournisseurs_data:  # Ne pas inclure les commodités sans fournisseurs
                # Trouver la date du dernier échantillon
                derniere_date = max(e.date_creation for e in echantillons_commodite)
                
                disponibilites.append({
                    'commodite': commodite,
                    'quantite_totale': quantite_totale,
                    'nombre_fournisseurs': len(fournisseurs_data),
                    'fournisseurs': fournisseurs_data,
                    'derniere_maj': derniere_date
                })
        
        # Trier les commodités par quantité totale décroissante
        disponibilites.sort(key=lambda x: x['quantite_totale'], reverse=True)
        
        # Calculer le nombre de commodités avec stock faible (quantité <= 50)
        low_stock_count = sum(1 for d in disponibilites if d['quantite_totale'] <= 50)
        
        # Ajouter les variables au contexte
        context['disponibilites'] = disponibilites
        context['total_tonnes'] = total_general  # Ajouter le total général au contexte
        context['toutes_commodites'] = commodites
        context['nombre_commodites'] = len(disponibilites)
        context['low_stock_count'] = low_stock_count
        
        return context