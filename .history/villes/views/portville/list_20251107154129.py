

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
