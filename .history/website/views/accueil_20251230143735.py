from django.views.generic import TemplateView
from echantillonnages.models import Echantionnage
from django.db.models import Max

class AccueilView(TemplateView):
    template_name = 'website/accueil.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Récupérer le dernier échantillon pour chaque commodité
        dernier_echantillon = Echantionnage.objects.values('commodite').annotate(
            dernier_id=Max('id')
        ).values_list('dernier_id', flat=True)
        
        echantillons = Echantionnage.objects.filter(
            id__in=dernier_echantillon
        ).select_related('commodite').order_by('commodite__nom')
        
        # Préparer les données pour le template
        commodites_disponibles = []
        for echantillon in echantillons:
            commodites_disponibles.append({
                'nom': echantillon.commodite.nom,
                'quantite': echantillon.quantite,
               
                'date_echantillonnage': echantillon.date_creation,  # Utilisation de date_creation au lieu de date_echantillonnage
                'disponible': echantillon.quantite > 0,
                'classe_css': 'disponible' if echantillon.quantite > 0 else 'indisponible'
            })
        
        context['commodites'] = commodites_disponibles
        context['titre'] = "Disponibilité des Commodités"
        context['sous_titre'] = "Dernières mises à jour des stocks"
        
        return context