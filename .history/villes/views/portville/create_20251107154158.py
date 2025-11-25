
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
