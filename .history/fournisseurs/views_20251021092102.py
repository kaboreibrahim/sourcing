

class FournisseurDetailView(LoginRequiredMixin, DetailView):
    """
    Vue pour afficher les détails d'un fournisseur avec ses commodités
    """
    model = Fournisseur
    template_name = 'fournisseur_detail.html'
    context_object_name = 'fournisseur'
    
    def get_queryset(self):
        return Fournisseur.objects.select_related(
            'ville',
            'ville__zone'
        ).prefetch_related(
            'liens_commodites',
            'liens_commodites__commodite'
        )
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        fournisseur = self.object
        
        # Récupérer toutes les commodités fournies
        liens = fournisseur.liens_commodites.filter(
            deleted__isnull=True
        ).select_related('commodite').order_by('commodite__nom')
        
        context['liens_commodites'] = liens
        context['total_commodites'] = liens.count()
        
        # Vérifier si le fournisseur a des coordonnées GPS
        context['has_coordinates'] = fournisseur.latitude and fournisseur.longitude
        
        return context


class FournisseurCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    """
    Vue pour créer un nouveau fournisseur
    """
    model = Fournisseur
    template_name = 'fournisseur_form.html'
    fields = [
        'nom', 'nom_responsable', 'contact', 'ville', 'localite',
        'latitude', 'longitude', 'distance_port_abidjan', 
        'distance_port_sanpedro', 'document_fourni_aex'
    ]
    success_message = _("Le fournisseur %(nom)s a été créé avec succès")
    
    def get_success_url(self):
        return reverse_lazy('fournisseur-detail', kwargs={'pk': self.object.pk})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _("Créer un nouveau fournisseur")
        context['button_text'] = _("Créer")
        
        # Si une ville est passée en paramètre
        ville_id = self.request.GET.get('ville')
        if ville_id:
            context['ville_preselected'] = ville_id
        
        return context


class FournisseurUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    """
    Vue pour modifier un fournisseur
    """
    model = Fournisseur
    template_name = 'fournisseur_form.html'
    fields = [
        'nom', 'nom_responsable', 'contact', 'ville', 'localite',
        'latitude', 'longitude', 'distance_port_abidjan', 
        'distance_port_sanpedro', 'document_fourni_aex'
    ]
    success_message = _("Le fournisseur %(nom)s a été modifié avec succès")
    
    def get_success_url(self):
        return reverse_lazy('fournisseur-detail', kwargs={'pk': self.object.pk})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _("Modifier %(nom)s") % {'nom': self.object.nom}
        context['button_text'] = _("Mettre à jour")
        return context


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
        context['total_commodites'] = self.object.liens_commodites.filter(
            deleted__isnull=True
        ).count()
        return context


# ============================================================
# VUES POUR STATISTIQUES ET CARTOGRAPHIE
# ============================================================

class FournisseurMapView(LoginRequiredMixin, ListView):
    """
    Vue pour afficher les fournisseurs sur une carte
    """
    model = Fournisseur
    template_name = 'fournisseur_map.html'
    context_object_name = 'fournisseurs'
    
    def get_queryset(self):
        # Récupérer uniquement les fournisseurs avec coordonnées GPS
        queryset = Fournisseur.objects.select_related(
            'ville',
            'ville__zone'
        ).filter(
            latitude__isnull=False,
            longitude__isnull=False,
            deleted__isnull=True
        ).annotate(
            total_commodites=Count('liens_commodites')
        )
        
        # Filtre par zone
        zone_id = self.request.GET.get('zone', '')
        if zone_id:
            queryset = queryset.filter(ville__zone_id=zone_id)
        
        # Filtre par commodité
        commodite_id = self.request.GET.get('commodite', '')
        if commodite_id:
            queryset = queryset.filter(liens_commodites__commodite_id=commodite_id)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Préparer les données pour la carte (format JSON)
        fournisseurs_data = []
        for fournisseur in context['fournisseurs']:
            fournisseurs_data.append({
                'id': str(fournisseur.id),
                'nom': fournisseur.nom,
                'latitude': float(fournisseur.latitude),
                'longitude': float(fournisseur.longitude),
                'ville': fournisseur.ville.nom,
                'zone': fournisseur.ville.zone.numero,
                'total_commodites': fournisseur.total_commodites,
                'url': reverse_lazy('fournisseur-detail', kwargs={'pk': fournisseur.pk})
            })
        
        context['fournisseurs_json'] = fournisseurs_data
        
        
        
        context['zones'] = Zone.objects.all().order_by('numero')
        context['selected_zone'] = self.request.GET.get('zone', '')
        
        context['commodites'] = Commodite.objects.all().order_by('nom')
        context['selected_commodite'] = self.request.GET.get('commodite', '')
        
        context['total_with_coordinates'] = len(fournisseurs_data)
        context['total_fournisseurs'] = Fournisseur.objects.count()
        
        return context


class FournisseurStatsView(LoginRequiredMixin, ListView):
    """
    Vue pour afficher des statistiques sur les fournisseurs
    """
    model = Fournisseur
    template_name = 'fournisseur_stats.html'
    context_object_name = 'fournisseurs'
    
    def get_queryset(self):
        return Fournisseur.objects.select_related(
            'ville',
            'ville__zone'
        ).annotate(
            total_commodites=Count(
                'liens_commodites',
                filter=Q(liens_commodites__deleted__isnull=True)
            )
        ).order_by('-total_commodites', 'nom')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Statistiques générales
        context['total_fournisseurs'] = Fournisseur.objects.count()
        context['total_with_coordinates'] = Fournisseur.objects.filter(
            latitude__isnull=False,
            longitude__isnull=False
        ).count()
        context['total_with_documents'] = Fournisseur.objects.exclude(
            document_fourni_aex=''
        ).exclude(
            document_fourni_aex__isnull=True
        ).count()
        
         
        
        context['total_zones'] = Zone.objects.count()
        context['total_villes'] = Ville.objects.count()
        context['total_commodites'] = Commodite.objects.count()
        context['total_liaisons'] = FournisseurCommodite.objects.filter(
            deleted__isnull=True
        ).count()
        
        # Fournisseur avec le plus de commodités
        top_fournisseur = Fournisseur.objects.annotate(
            nb_commodites=Count('liens_commodites')
        ).order_by('-nb_commodites').first()
        
        context['top_fournisseur'] = top_fournisseur
        
        # Statistiques par zone
        from django.db.models import Count as CountFunc
        zones_data = Zone.objects.annotate(
            nb_fournisseurs=CountFunc('villes__fournisseurs', distinct=True),
            nb_commodites=CountFunc(
                'villes__fournisseurs__liens_commodites__commodite',
                distinct=True
            )
        ).order_by('numero')
        
        context['zones_data'] = zones_data
        
        # Répartition par ville (top 10)
        villes_data = Ville.objects.annotate(
            nb_fournisseurs=CountFunc('fournisseurs')
        ).filter(
            nb_fournisseurs__gt=0
        ).order_by('-nb_fournisseurs')[:10]
        
        context['villes_data'] = villes_data
        
        return context


# ============================================================
# VUE POUR RECHERCHE AVANCÉE
# ============================================================

class FournisseurSearchView(LoginRequiredMixin, ListView):
    """
    Vue pour la recherche avancée de fournisseurs
    """
    model = Fournisseur
    template_name = 'fournisseur_search.html'
    context_object_name = 'fournisseurs'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Fournisseur.objects.select_related(
            'ville',
            'ville__zone'
        ).annotate(
            total_commodites=Count('liens_commodites')
        )
        
        # Recherche par nom
        nom = self.request.GET.get('nom', '')
        if nom:
            queryset = queryset.filter(nom__icontains=nom)
        
        # Recherche par responsable
        responsable = self.request.GET.get('responsable', '')
        if responsable:
            queryset = queryset.filter(nom_responsable__icontains=responsable)
        
        # Filtre par zone
        zone_id = self.request.GET.get('zone', '')
        if zone_id:
            queryset = queryset.filter(ville__zone_id=zone_id)
        
        # Filtre par ville
        ville_id = self.request.GET.get('ville', '')
        if ville_id:
            queryset = queryset.filter(ville_id=ville_id)
        
        # Filtre par commodité
        commodite_id = self.request.GET.get('commodite', '')
        if commodite_id:
            queryset = queryset.filter(liens_commodites__commodite_id=commodite_id)
        
        # Filtre par présence de coordonnées GPS
        has_gps = self.request.GET.get('has_gps', '')
        if has_gps == 'yes':
            queryset = queryset.filter(
                latitude__isnull=False,
                longitude__isnull=False
            )
        elif has_gps == 'no':
            queryset = queryset.filter(
                Q(latitude__isnull=True) | Q(longitude__isnull=True)
            )
        
        # Filtre par présence de documents
        has_doc = self.request.GET.get('has_doc', '')
        if has_doc == 'yes':
            queryset = queryset.exclude(document_fourni_aex='').exclude(
                document_fourni_aex__isnull=True
            )
        elif has_doc == 'no':
            queryset = queryset.filter(
                Q(document_fourni_aex='') | Q(document_fourni_aex__isnull=True)
            )
        
        return queryset.order_by('nom')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
       
        
        context['zones'] = Zone.objects.all().order_by('numero')
        context['villes'] = Ville.objects.select_related('zone').order_by('nom')
        context['commodites'] = Commodite.objects.all().order_by('nom')
        
        # Conserver les valeurs des filtres
        context['search_params'] = {
            'nom': self.request.GET.get('nom', ''),
            'responsable': self.request.GET.get('responsable', ''),
            'zone': self.request.GET.get('zone', ''),
            'ville': self.request.GET.get('ville', ''),
            'commodite': self.request.GET.get('commodite', ''),
            'has_gps': self.request.GET.get('has_gps', ''),
            'has_doc': self.request.GET.get('has_doc', ''),
        }
        
        context['total_results'] = self.get_queryset().count()
        
        return context