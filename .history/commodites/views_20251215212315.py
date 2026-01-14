from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.db.models import Count, Q, Prefetch
from django.contrib.auth.mixins import LoginRequiredMixin
from commodites.models import Commodite, FournisseurCommodite


# ============================================================
# VUES POUR LA LISTE DE COMMODITE
# ============================================================

class CommoditeListView(LoginRequiredMixin, ListView):
    """
    Vue pour afficher la liste des commodités sous forme de cards
    avec statistiques sur les fournisseurs
    """
    model = Commodite
    template_name = 'commodite_list.html'
    context_object_name = 'commodites'
    paginate_by = 12
    
    def get_queryset(self):
        """
        Optimisation avec annotation du nombre de fournisseurs
        """
        queryset = Commodite.objects.annotate(
            total_fournisseurs=Count(
                'liens_fournisseurs',
                filter=Q(liens_fournisseurs__deleted__isnull=True)
            )
        ).prefetch_related(
            Prefetch(
                'liens_fournisseurs',
                queryset=FournisseurCommodite.objects.select_related(
                    'fournisseur',
                    'fournisseur__ville',
                    'fournisseur__ville__zone'
                ).filter(deleted__isnull=True)
            )
        ).order_by('nom')
        
        # Filtre de recherche
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(nom__icontains=search_query)
            )
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        context['total_commodites'] = Commodite.objects.count()
        
        # Statistiques globales
        context['total_liaisons'] = FournisseurCommodite.objects.filter(
            deleted__isnull=True
        ).count()
        
        return context


# ============================================================
# VUES POUR LA COMMODITE DETAIL
# ============================================================


class CommoditeDetailView(LoginRequiredMixin, DetailView):
    """
    Vue pour afficher les détails d'une commodité avec la liste de ses fournisseurs
    """
    model = Commodite
    template_name = 'commodite_detail.html'
    context_object_name = 'commodite'
    
    def get_queryset(self):
        return Commodite.objects.prefetch_related(
            'liens_fournisseurs',
            'liens_fournisseurs__fournisseur',
            'liens_fournisseurs__fournisseur__ville',
            'liens_fournisseurs__fournisseur__ville__zone'
        )
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        commodite = self.object
        
        # Récupérer le paramètre de zone depuis l'URL
        zone_num = self.request.GET.get('zone')
        
        # Base query pour les liens fournisseurs
        liens_query = commodite.liens_fournisseurs.filter(
            deleted__isnull=True
        ).select_related(
            'fournisseur',
            'fournisseur__ville',
            'fournisseur__ville__zone'
        ).order_by('fournisseur__nom')
        
        # Filtrer par zone si spécifiée
        if zone_num and zone_num.isdigit():
            zone_num = int(zone_num)
            liens_query = liens_query.filter(
                fournisseur__ville__zone__numero=zone_num
            )
            context['zone_active'] = zone_num
        
        # Préparer les données pour le template
        context['liens_fournisseurs'] = liens_query
        context['total_fournisseurs'] = liens_query.count()
        
        # Pour les statistiques, on prend tous les fournisseurs (sans filtre de zone)
        liens_tous = commodite.liens_fournisseurs.filter(
            deleted__isnull=True,
            fournisseur__ville__zone__isnull=False
        ).select_related(
            'fournisseur',
            'fournisseur__ville',
            'fournisseur__ville__zone'
        )
        
        # Statistiques par zone
        zones_stats = {}
        for lien in liens_tous:
            if lien.fournisseur.ville and lien.fournisseur.ville.zone:
                zone_num = lien.fournisseur.ville.zone.numero
                if zone_num not in zones_stats:
                    zones_stats[zone_num] = {
                        'zone': lien.fournisseur.ville.zone,
                        'count': 0,
                        'villes': set(),
                        'url': f'?zone={zone_num}'
                    }
                    
                    # Si c'est la zone active, on l'ajoute dans l'URL
                    if 'zone_active' in context and context['zone_active'] == zone_num:
                        zones_stats[zone_num]['is_active'] = True
                
                zones_stats[zone_num]['count'] += 1
                zones_stats[zone_num]['villes'].add(lien.fournisseur.ville.nom)
        
        # Trier les zones par numéro
        context['zones_stats'] = dict(sorted(zones_stats.items()))
        
        # Lien pour réinitialiser le filtre
        if 'zone_active' in context:
            context['reset_filter_url'] = self.request.path
        
        return context


# ============================================================
# VUES POUR LA COMMODITE CREATE
# ============================================================

class CommoditeCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    """
    Vue pour créer une nouvelle commodité
    """
    model = Commodite
    template_name = 'commodite_form.html'
    fields = ['nom']
    success_message = _("La commodité %(nom)s a été créée avec succès")
    
    def get_success_url(self):
        return reverse_lazy('commodite-detail', kwargs={'pk': self.object.pk})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _("Créer une nouvelle commodité")
        context['button_text'] = _("Créer")
        return context


# ============================================================
# VUES POUR LA COMMODITE UPDATE
# ============================================================

class CommoditeUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    """
    Vue pour modifier une commodité
    """
    model = Commodite
    template_name = 'commodite_form.html'
    fields = ['nom', 'couleur']  # Ajoutez 'couleur' ici
    success_message = _("La commodité %(nom)s a été modifiée avec succès")
    
    def get_success_url(self):
        return reverse_lazy('commodite-detail', kwargs={'pk': self.object.pk})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _("Modifier %(nom)s") % {'nom': self.object.nom}
        context['button_text'] = _("Mettre à jour")
        return context


# ============================================================
# VUES POUR LA COMMODITE DELETE
# ============================================================

class CommoditeDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    """
    Vue pour supprimer une commodité (suppression logique avec safedelete)
    """
    model = Commodite
    template_name = 'commodite_confirm_delete.html'
    fields = ['nom', 'couleur']  # Ajoutez 'couleur' ici
    success_url = reverse_lazy('commodite-list')
    success_message = _("La commodité a été supprimée avec succès")
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_fournisseurs'] = self.object.liens_fournisseurs.filter(
            deleted__isnull=True
        ).count()
        return context


# ============================================================
# VUES POUR FOURNISSEUR-COMMODITE (Liaison)
# ============================================================

class FournisseurCommoditeListView(LoginRequiredMixin, ListView):
    """
    Vue pour afficher la liste des liaisons fournisseur-commodité
    """
    model = FournisseurCommodite
    template_name = 'fournisseur_commodite_list.html'
    context_object_name = 'liaisons'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = FournisseurCommodite.objects.select_related(
            'fournisseur',
            'fournisseur__ville',
            'fournisseur__ville__zone',
            'commodite'
        ).filter(deleted__isnull=True).order_by(
            'commodite__nom',
            'fournisseur__nom'
        )
        
        # Filtre de recherche
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(fournisseur__nom__icontains=search_query) |
                Q(commodite__nom__icontains=search_query) |
                Q(fournisseur__ville__nom__icontains=search_query)
            )
        
        # Filtre par commodité
        commodite_id = self.request.GET.get('commodite', '')
        if commodite_id:
            queryset = queryset.filter(commodite_id=commodite_id)
        
        # Filtre par zone
        zone_id = self.request.GET.get('zone', '')
        if zone_id:
            queryset = queryset.filter(fournisseur__ville__zone_id=zone_id)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        context['commodites'] = Commodite.objects.all().order_by('nom')
        context['selected_commodite'] = self.request.GET.get('commodite', '')
        
        # Import Zone pour le filtre
        from zones.models import Zone
        context['zones'] = Zone.objects.all().order_by('numero')
        context['selected_zone'] = self.request.GET.get('zone', '')
        
        context['total_liaisons'] = FournisseurCommodite.objects.filter(
            deleted__isnull=True
        ).count()
        
        return context


# ============================================================
# VUES POUR LA FournisseurCommodite CREATE
# ============================================================

class FournisseurCommoditeCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    """
    Vue pour créer une nouvelle liaison fournisseur-commodité
    """
    model = FournisseurCommodite
    template_name = 'fournisseur_commodite_form.html'
    fields = ['fournisseur', 'commodite']
    success_message = _("La liaison a été créée avec succès")
    
    def get_success_url(self):
        # Rediriger vers le détail de la commodité
        return reverse_lazy('commodite-detail', kwargs={'pk': self.object.commodite.pk})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _("Créer une liaison Fournisseur-Commodité")
        context['button_text'] = _("Créer")
        
        # Si une commodité est passée en paramètre
        commodite_id = self.request.GET.get('commodite')
        if commodite_id:
            context['commodite_preselected'] = commodite_id
        
        # Si un fournisseur est passé en paramètre
        fournisseur_id = self.request.GET.get('fournisseur')
        if fournisseur_id:
            context['fournisseur_preselected'] = fournisseur_id
        
        return context
    
    def form_valid(self, form):
        # Vérifier si la liaison existe déjà
        fournisseur = form.cleaned_data['fournisseur']
        commodite = form.cleaned_data['commodite']
        
        existing = FournisseurCommodite.objects.filter(
            fournisseur=fournisseur,
            commodite=commodite,
            deleted__isnull=True
        ).first()
        
        if existing:
            form.add_error(
                None,
                _("Cette liaison existe déjà entre %(fournisseur)s et %(commodite)s") % {
                    'fournisseur': fournisseur.nom,
                    'commodite': commodite.nom
                }
            )
            return self.form_invalid(form)
        
        return super().form_valid(form)


# ============================================================
# VUES POUR LA FournisseurCommodite DELETE
# ============================================================

class FournisseurCommoditeDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    """
    Vue pour supprimer une liaison fournisseur-commodité
    """
    model = FournisseurCommodite
    template_name = 'fournisseur_commodite_confirm_delete.html'
    success_message = _("La liaison a été supprimée avec succès")
    
    def get_success_url(self):
        # Rediriger vers le détail de la commodité
        return reverse_lazy('commodite-detail', kwargs={'pk': self.object.commodite.pk})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


# ============================================================
# VUE POUR STATISTIQUES GLOBALES
# ============================================================

class CommoditeStatsView(LoginRequiredMixin, ListView):
    """
    Vue pour afficher des statistiques globales sur les commodités
    """
    model = Commodite
    template_name = 'commodite_stats.html'
    context_object_name = 'commodites'
    
    def get_queryset(self):
        return Commodite.objects.annotate(
            total_fournisseurs=Count(
                'liens_fournisseurs',
                filter=Q(liens_fournisseurs__deleted__isnull=True)
            )
        ).order_by('-total_fournisseurs', 'nom')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Statistiques générales
        context['total_commodites'] = Commodite.objects.count()
        context['total_liaisons'] = FournisseurCommodite.objects.filter(
            deleted__isnull=True
        ).count()
        
        # Import des modèles nécessaires
        from fournisseurs.models import Fournisseur
        from zones.models import Zone
        
        context['total_fournisseurs'] = Fournisseur.objects.count()
        context['total_zones'] = Zone.objects.count()
        
        # Commodité la plus fournie
        top_commodite = Commodite.objects.annotate(
            nb_fournisseurs=Count('liens_fournisseurs')
        ).order_by('-nb_fournisseurs').first()
        
        context['top_commodite'] = top_commodite
        
        # Statistiques par zone
        from django.db.models import Count as CountFunc
        zones_data = Zone.objects.annotate(
            nb_commodites=CountFunc(
                'villes__fournisseurs__liens_commodites__commodite',
                distinct=True
            ),
            nb_fournisseurs=CountFunc(
                'villes__fournisseurs',
                distinct=True
            )
        ).order_by('numero')
        
        context['zones_data'] = zones_data
        
        return context