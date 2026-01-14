

from django.views.generic import TemplateView
class AccueilFournisseurView(TemplateView):
    template_name = 'website/accueil.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Ajoutez ici les données que vous voulez passer au template
        context['titre'] = 'Bienvenue sur Sourcing'
        context['sous_titre'] = 'Votre plateforme de gestion des fournisseurs'
        return context