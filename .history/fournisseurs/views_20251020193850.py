from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.db.models import Count, Q, Prefetch
from django.contrib.auth.mixins import LoginRequiredMixin
from commodites.models import  FournisseurCommodite ,Commodite 
from fournisseurs.models import Fournisseur


# ============================================================
# VUES POUR LA LISTE DES FOURNISSEURS
# ============================================================

class FournisseurListView(LoginRequiredMixin, ListView):
    """
    Vue pour afficher la liste des fournisseurs avec des statistiques
    """
    model = Fournisseur
    template_name = 'fournisseur_list.html'
    context_object_name = 'fournisseurs'
    paginate_by = 12
    
    def get_queryset(self):
        """
        Optimisation avec annotation du nombre de commodités
        """
        queryset = Fournisseur.objects.annotate(
            total_commodites=Count(
                'liens_commodites',
                filter=Q(liens_commodites__deleted__isnull=True)
            )
        ).prefetch_related(
            'ville',
            'ville__zone',
            Prefetch(
                'liens_commodites',
                queryset=FournisseurCommodite.objects.select_related('commodite')
                .filter(deleted__isnull=True)
            )
        ).order_by('nom')
        
        # Filtre de recherche
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(nom__icontains=search_query) |
                Q(nom_responsable__icontains=search_query) |
                Q(ville__nom__icontains=search_query) |
                Q(localite__icontains=search_query)
            )
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        context['total_fournisseurs'] = Fournisseur.objects.count()
        
        # Statistiques globales
        context['total_liaisons'] = FournisseurCommodite.objects.filter(
            deleted__isnull=True
        ).count()
        
        return context


# ============================================================
# VUE POUR LES DÉTAILS D'UN FOURNISSEUR
# ============================================================

class FournisseurDetailView(LoginRequiredMixin, DetailView):
    """
    Vue pour afficher les détails d'un fournisseur avec la liste de ses commodités
    """
    model = Fournisseur
    template_name = 'fournisseur_detail.html'
    context_object_name = 'fournisseur'
    
    def get_queryset(self):
        return Fournisseur.objects.prefetch_related(
            'ville',
            'ville__zone',
            Prefetch(
                'liens_commodites',
                queryset=FournisseurCommodite.objects.select_related('commodite')
                .filter(deleted__isnull=True)
            )
        )
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        fournisseur = self.object
        
        # Récupérer les commodités non liées pour le formulaire d'ajout
        commodites_liees = fournisseur.liens_commodites.filter(
            deleted__isnull=True
        ).values_list('commodite_id', flat=True)
        
        context['commodites_disponibles'] = Commodite.objects.exclude(
            id__in=commodites_liees
        )
        
        return context


# ============================================================
# VUE POUR CRÉER UN FOURNISSEUR
# ============================================================

class FournisseurCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    """
    Vue pour créer un nouveau fournisseur
    """
    model = Fournisseur
    template_name = 'fournisseur_form.html'
    fields = [
        'nom', 'nom_responsable', 'contact', 'ville', 'localite',
        'latitude', 'longitude', 'distance_port_abidjan', 'distance_port_sanpedro',
        'document_fourni_aex'
    ]
    success_message = _("Le fournisseur %(nom)s a été créé avec succès")
    
    def get_success_url(self):
        return reverse_lazy('fournisseur-detail', kwargs={'pk': self.object.pk})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titre'] = _("Ajouter un fournisseur")
        context['bouton_soumettre'] = _("Créer")
        return context


# ============================================================
# VUE POUR MODIFIER UN FOURNISSEUR
# ============================================================

class FournisseurUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    """
    Vue pour modifier un fournisseur existant
    """
    model = Fournisseur
    template_name = 'fournisseur_form.html'
    fields = [
        'nom', 'nom_responsable', 'contact', 'ville', 'localite',
        'latitude', 'longitude', 'distance_port_abidjan', 'distance_port_sanpedro',
        'document_fourni_aex'
    ]
    success_message = _("Le fournisseur %(nom)s a été modifié avec succès")
    
    def get_success_url(self):
        return reverse_lazy('fournisseur-detail', kwargs={'pk': self.object.pk})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titre'] = _("Modifier le fournisseur")
        context['bouton_soumettre'] = _("Mettre à jour")
        return context


# ============================================================
# VUE POUR SUPPRIMER UN FOURNISSEUR
# ============================================================

class FournisseurDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    """
    Vue pour supprimer un fournisseur (suppression logique avec safedelete)
    """
    model = Fournisseur
    template_name = 'fournisseur_confirm_delete.html'
    success_url = reverse_lazy('fournisseur-list')
    success_message = _("Le fournisseur a été supprimé avec succès")
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titre'] = _("Confirmer la suppression")
        context['message'] = _("Êtes-vous sûr de vouloir supprimer ce fournisseur ?")
        return context