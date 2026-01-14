from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from commodites.models import Commodite, FournisseurCommodite
from echantillonnages.models import Echantionnage
from django.core.exceptions import PermissionDenied
from django.db.models import Prefetch, Sum, Count, F, FloatField
from django.db.models.functions import Coalesce

class UpdateDisponibiliteCommoditeView(LoginRequiredMixin, UpdateView):
    """
    Vue pour mettre à jour la disponibilité d'une commodité pour un fournisseur
    """
    model = FournisseurCommodite
    form_class = FournisseurCommoditeForm
    template_name = 'fournisseur/update_disponibilite.html'
    context_object_name = 'lien_fournisseur'
    
    def get_object(self, queryset=None):
        """Récupère l'objet FournisseurCommodite ou retourne une 404"""
        commodite_id = self.kwargs.get('pk')
        user = self.request.user
        
        if not hasattr(user, 'fournisseur_profile'):
            raise PermissionDenied("Accès réservé aux fournisseurs")
            
        return get_object_or_404(
            FournisseurCommodite,
            commodite_id=commodite_id,
            fournisseur=user.fournisseur_profile,
            is_active=True
        )
    
    def get_success_url(self):
        messages.success(self.request, "Disponibilité mise à jour avec succès!")
        return reverse_lazy('fournisseur:accueil')
    
    def form_valid(self, form):
        """Ajoute le fournisseur au formulaire avant la validation"""
        form.instance.fournisseur = self.request.user.fournisseur_profile
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['commodite'] = self.object.commodite
        return context


class AccueilFournisseurView(LoginRequiredMixin, ListView):
    model = Commodite
    template_name = 'fournisseur/accueil.html'
    context_object_name = 'commodites'

    def get_queryset(self):
        user = self.request.user

        if user.type_user != 'FS':
            raise PermissionDenied("Accès réservé aux fournisseurs")

        fournisseur = getattr(user, 'fournisseur_profile', None)
        if not fournisseur:
            return Commodite.objects.none()

        # Récupérer d'abord les commodités liées au fournisseur
        commodites = (
            Commodite.objects
            .filter(liens_fournisseurs__fournisseur=fournisseur)
            .prefetch_related(
                Prefetch(
                    'echantillonnages',
                    queryset=Echantionnage.objects
                        .filter(fournisseur=fournisseur)
                        .order_by('-date_creation')
                ),
                'liens_fournisseurs'
            )
            .distinct()
        )

        # Ajouter les annotations manuellement
        for commodite in commodites:
            # Calculer la quantité totale
            quantite_totale = sum(
                float(lf.quantite_disponible) 
                for lf in commodite.liens_fournisseurs.all() 
                if hasattr(lf, 'quantite_disponible') and lf.quantite_disponible is not None
            )
            
            # Calculer le prix moyen
            prix_unitaire = [
                float(lf.prix_unitaire) 
                for lf in commodite.liens_fournisseurs.all() 
                if hasattr(lf, 'prix_unitaire') and lf.prix_unitaire is not None
            ]
            prix_moyen = sum(prix_unitaire) / len(prix_unitaire) if prix_unitaire else 0

            # Ajouter les attributs dynamiques
            commodite.quantite_totale = quantite_totale
            commodite.prix_moyen = prix_moyen

        return commodites