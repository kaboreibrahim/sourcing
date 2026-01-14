from django.shortcuts import render, get_object_or_404
from django.db.models import Sum, Max
from django.views.generic import ListView
from echantillonnages.models import Echantionnage
from commodites.models import Commodite

class AccueilView(ListView):
    model = Echantionnage
    template_name = 'website/accueil.html'
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
        
        # Get the queryset
        queryset = self.get_queryset()
        
        # Calculate total quantity for the commodity
        quantite_totale = sum(
            e.quantite for e in queryset if hasattr(e, 'quantite')
        )
        
        context.update({
            'commodite': getattr(self, 'commodite', None),
            'quantite_totale': quantite_totale,
            'titre_page': f"Disponibilité - {getattr(self.commodite, 'nom', '')}"
        })
        
        return context