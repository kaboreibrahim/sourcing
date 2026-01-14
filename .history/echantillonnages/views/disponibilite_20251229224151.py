from django.shortcuts import render, get_object_or_404
from django.db.models import Sum, Max
from django.views.generic import ListView
from echantillonnages.models import Echantionnage
from commodites.models import Commodite

class DisponibiliteCommoditeView(ListView):
    model = Echantionnage
    template_name = 'disponibilite/disponibilite_commodite.html'
    context_object_name = 'echantillons'

    def get_queryset(self):
        # Récupérer l'ID de la commodité depuis l'URL
        self.commodite_id = self.kwargs.get('commodite_id')
        
        # Récupérer la commodité
        self.commodite = get_object_or_404(Commodite, id=self.commodite_id)
        
        # Récupérer le dernier échantillon pour chaque fournisseur
        derniers_echantillons = Echantionnage.objects.filter(
            commodite_id=self.commodite_id
        ).values('fournisseur').annotate(
            derniere_date=Max('date_creation')
        )
        
        # Créer une liste des IDs des derniers échantillons
        echantillon_ids = []
        for item in derniers_echantillons:
            echantillon = Echantionnage.objects.filter(
                fournisseur_id=item['fournisseur'],
                date_creation=item['derniere_date']
            ).first()
            if echantillon:
                echantillon_ids.append(echantillon.id)
        
        # Retourner les échantillons complets
        return Echantionnage.objects.filter(
            id__in=echantillon_ids
        ).select_related('fournisseur').order_by('fournisseur__nom')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Calculer la quantité totale pour la commodité
        quantite_totale = sum(
            e.quantite for e in self.object_list
        )
        
        context.update({
            'commodite': self.commodite,
            'quantite_totale': quantite_totale,
            'titre_page': f"Disponibilité - {self.commodite.nom}"
        })
        
        return context

from django.db.models import Sum, Subquery, OuterRef
from django.views.generic import TemplateView
from echantillonnages.models import Echantionnage
from commodites.models import Commodite

class ListeDisponibilitesView(TemplateView):
    template_name = 'disponibilite/liste_disponibilites.html'
    
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
                disponibilites.append({
                    'commodite': commodite,
                    'quantite_totale': quantite_totale,
                    'nombre_fournisseurs': len(fournisseurs_data),
                    'fournisseurs': fournisseurs_data
                })
        
        # Trier les commodités par quantité totale décroissante
        disponibilites.sort(key=lambda x: x['quantite_totale'], reverse=True)
        
        # Ajouter les variables au contexte
        context['disponibilites'] = disponibilites
        context['total_general'] = total_general
        context['nombre_commodites'] = len(disponibilites)
        
        return context