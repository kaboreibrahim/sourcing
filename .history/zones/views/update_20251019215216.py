
class ZoneUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    """
    Vue pour modifier une zone
    """
    model = Zone
    template_name = 'zones/zone_form.html'
    fields = ['description']
    success_message = _("La zone %(numero)s a été modifiée avec succès")
    
    def get_success_url(self):
        return reverse_lazy('zone-detail', kwargs={'pk': self.object.pk})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _("Modifier la zone %(numero)s") % {'numero': self.object.numero}
        context['button_text'] = _("Mettre à jour")
        return context