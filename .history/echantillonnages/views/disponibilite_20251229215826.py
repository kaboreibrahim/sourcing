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



# echantillonnages/views/disponibilite.py
from django.shortcuts import render, get_object_or_404
from django.db.models import Sum, Max, Subquery, OuterRef
from django.views.generic import ListView, TemplateView
from echantillonnages.models import Echantionnage
from commodites.models import Commodite

class ListeDisponibilitesView(TemplateView):
    template_name = 'disponibilite/liste_disponibilites.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Sous-requête pour obtenir le dernier échantillon par commodité et fournisseur
        derniers_echantillons = Echantionnage.objects.filter(
            commodite=OuterRef('pk'),
            fournisseur=OuterRef('fournisseur__id')
        ).order_by('-date_creation')
        
        # Récupérer toutes les commodités avec leur quantité totale
        commodites = Commodite.objects.annotate(
            quantite_totale=Sum('echantillonnages__quantite')
        ).prefetch_related('echantillonnages__fournisseur')
        
        # Préparer les données pour le template
        disponibilites = []
        for commodite in commodites:
            # Récupérer la liste des fournisseurs avec leur dernière quantité
            fournisseurs = []
            for echantillon in commodite.echantillonnages.all().order_by('-date_creation'):
                # Vérifier si ce fournisseur a déjà été ajouté
                if not any(f['id'] == str(echantillon.fournisseur.id) for f in fournisseurs):
                    fournisseurs.append({
                        'id': str(echantillon.fournisseur.id),
                        'nom': echantillon.fournisseur.nom,
                        'quantite': echantillon.quantite,
                        'date': echantillon.date_creation
                    })
            
            disponibilites.append({
                'commodite': commodite,
                'quantite_totale': commodite.quantite_totale or 0,
                'nombre_fournisseurs': len(fournisseurs),
                'fournisseurs': fournisseurs[:3]  # Afficher seulement les 3 premiers fournisseurs
            })
        
        context['disponibilites'] = disponibilites
        return context

