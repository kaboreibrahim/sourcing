from django.views.generic import TemplateView
from echantillonnages.models import Echantionnage
from django.db.models import Max, Subquery, OuterRef

class AccueilView(TemplateView):
    template_name = 'website/accueil.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Sous-requête pour obtenir le dernier ID d'échantillon par commodité
        derniers_ids = Echantionnage.objects.filter(
            commodite_id=OuterRef('commodite_id')
        ).order_by('-date_creation').values('id')[:1]

        # Récupérer les échantillons les plus récents pour chaque commodité
        echantillons = Echantionnage.objects.filter(
            id__in=Subquery(derniers_ids)
        ).select_related('commodite').order_by('commodite__nom')
        
        # Préparer les données pour le template
        commodites_disponibles = []
        for echantillon in echantillons:
            commodites_disponibles.append({
                'nom': echantillon.commodite.nom,
                'quantite': echantillon.quantite,
                'date_echantillonnage': echantillon.date_creation,
                'disponible': echantillon.quantite > 0,
                'classe_css': 'disponible' if echantillon.quantite > 0 else 'indisponible'
            })
        
        context['commodites'] = commodites_disponibles
        context['titre'] = "Disponibilité des Commodités"
        context['sous_titre'] = "Dernières mises à jour des stocks"
        
        return context