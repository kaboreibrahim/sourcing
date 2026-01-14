from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView
from commodites.models import Commodite
from echantillonnages.models import Echantionnage
from django.core.exceptions import PermissionDenied
from django.db.models import Prefetch, Sum, Avg,Count,Min,Max
from django.http import JsonResponse
from echantillonnages.forms import EchantionnageForm

class DetailCommoditeFournisseurView(LoginRequiredMixin, DetailView):
    model = Commodite
    template_name = 'echantillons/detail_commodite.html'
    context_object_name = 'commodite'

    def get_queryset(self):
        user = self.request.user
        
        if user.type_user != 'FS':
            raise PermissionDenied("Accès réservé aux fournisseurs")
        
        fournisseur = getattr(user, 'fournisseur_profile', None)
        if not fournisseur:
            return Commodite.objects.none()
        
        return (
            Commodite.objects
            .filter(liens_fournisseurs__fournisseur=fournisseur)
            .prefetch_related(
                Prefetch(
                    'echantillonnages',
                    queryset=Echantionnage.objects
                        .filter(fournisseur=fournisseur)
                        .select_related('utilisateur')
                        .order_by('-date_creation')
                )
            )
            .distinct()
        )
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        commodite = self.object
        fournisseur = self.request.user.fournisseur_profile
        
       
        # Initialiser le formulaire avec l'utilisateur et la commodité
        form = EchantionnageForm(
            user=self.request.user,
            commodite=commodite
        )
        
        # Récupérer tous les échantillons
        echantillons = commodite.echantillonnages.filter(
            fournisseur=fournisseur
        ).order_by('-date_creation')
        
        
        # Préparer les données pour les graphiques
        dates = []
        quantites = []
        prix = []
        quantites_cumulees = []
        cumul = 0
        
        for ech in echantillons:
            dates.append(ech.date_creation.strftime('%d/%m/%Y'))
            quantites.append(float(ech.quantite))
            prix.append(float(ech.prix) if ech.prix else 0)
            cumul += float(ech.quantite)
            quantites_cumulees.append(cumul)
        
        context['chart_data'] = {
            'dates': dates,
            'quantites': quantites,
            'prix': prix,
            'quantites_cumulees': quantites_cumulees,
        }
        
        # Statistiques globales
        stats = echantillons.aggregate(
            quantite_totale=Sum('quantite'),
            prix_moyen=Avg('prix'),
            nombre_echantillons=Count('id')
        )
        
        context['stats'] = {
            'quantite_totale': stats['quantite_totale'] or 0,
            'prix_moyen': stats['prix_moyen'] or 0,
            'nombre_echantillons': stats['nombre_echantillons'] or 0,
            'prix_min': echantillons.aggregate(Min('prix'))['prix__min'] or 0,
            'prix_max': echantillons.aggregate(Max('prix'))['prix__max'] or 0,
        }
        
        context['echantillons'] = echantillons
        
        return context