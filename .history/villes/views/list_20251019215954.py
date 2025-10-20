# ============================================================
# VUES POUR VILLE
# ============================================================

class VilleListView(LoginRequiredMixin, ListView):
    """
    Vue pour afficher la liste de toutes les villes
    """
    model = Ville
    template_name = 'villes/ville_list.html'
    context_object_name = 'villes'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Ville.objects.select_related('zone').order_by(
            '-est_ville_reference',  # Villes de référence en premier
            'zone__numero',
            'nom'
        )
        
        # Filtre de recherche
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(nom__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(zone__numero__icontains=search_query)
            )
        
        # Filtre par zone
        zone_id = self.request.GET.get('zone', '')
        if zone_id:
            queryset = queryset.filter(zone_id=zone_id)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        context['zones'] = Zone.objects.all().order_by('numero')
        context['selected_zone'] = self.request.GET.get('zone', '')
        context['total_villes'] = Ville.objects.count()
        return context
