from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from simple_history.admin import SimpleHistoryAdmin
from safedelete.admin import SafeDeleteAdmin, highlight_deleted
from .models import Zone


@admin.register(Zone)
class ZoneAdmin(SimpleHistoryAdmin, SafeDeleteAdmin):
    """
    Interface d'administration pour le modèle Zone.
    Intègre l'historique (simple_history) et la suppression logique (safedelete).
    """
    
    # Colonnes affichées dans la liste
    list_display = (
        'numero',
        'description',
        'pays',
        'nombre_villes_display',
        'ville_reference_display',
        'created_at',
        'updated_at',
        highlight_deleted,
    )
    
    # Champs de recherche
    search_fields = ('numero', 'description','pays')
    
    # Filtres latéraux
    list_filter = (
        'created_at',
        'updated_at',
        'deleted',
    )
    
    # Champs en lecture seule
    readonly_fields = (
        'id',
        'numero',
        'pays',
        'created_at',
        'updated_at',
        'nombre_villes_display',
        'ville_reference_display',
    )
    
    # Organisation des champs dans le formulaire
    fieldsets = (
        (_('Informations principales'), {
            'fields': ('id', 'numero', 'description','pays')
        }),
        (_('Statistiques'), {
            'fields': ('nombre_villes_display', 'ville_reference_display'),
            'classes': ('collapse',),
        }),
        (_('Dates'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
    
    # Ordre de tri par défaut
    ordering = ('numero',)
    
    # Pagination
    list_per_page = 25
    
    # Affichage du nombre de villes
    @admin.display(description=_('Nombre de villes'))
    def nombre_villes_display(self, obj):
        """Affiche le nombre de villes dans la zone"""
        return obj.nombre_villes
    
    # Affichage de la ville de référence
    @admin.display(description=_('Ville de référence'))
    def ville_reference_display(self, obj):
        """Affiche la ville de référence de la zone"""
        ville_ref = obj.ville_reference
        return ville_ref.nom if ville_ref else _('Aucune')
    
    def has_delete_permission(self, request, obj=None):
        """
        Personnalisation des permissions de suppression.
        Vous pouvez ajouter une logique personnalisée ici.
        """
        return super().has_delete_permission(request, obj)
    
    def get_queryset(self, request):
        """
        Optimisation des requêtes avec prefetch_related
        pour éviter les problèmes N+1
        """
        qs = super().get_queryset(request)
        return qs.prefetch_related('villes')
    
  
  