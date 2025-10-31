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
