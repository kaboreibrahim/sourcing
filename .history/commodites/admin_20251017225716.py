from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from simple_history.admin import SimpleHistoryAdmin
from .models import Commodite, FournisseurCommodite


class FournisseurCommoditeInline(admin.TabularInline):
    """
    Inline pour gérer les fournisseurs d'une commodité
    """
    model = FournisseurCommodite
    extra = 1
    autocomplete_fields = ['fournisseur']
    readonly_fields = ['created_at', 'updated_at']
    
    fields = ['fournisseur', 'created_at']
    
    verbose_name = _("Fournisseur")
    verbose_name_plural = _("Fournisseurs de cette commodité")


@admin.register(Commodite)
class CommoditeAdmin(SimpleHistoryAdmin):
    """
    Administration du modèle Commodite
    """
    list_display = [
        'nom',
        'nombre_echantillons',
        'created_at',
        'updated_at',
    ]
    
    list_filter = [
        'created_at',
        'updated_at',
    ]
    
    search_fields = [
        'nom',
        'liens_fournisseurs__fournisseur__nom',
    ]
    
    readonly_fields = [
        'id',
        'created_at',
        'updated_at',
        'nombre_fournisseurs_display',
        'liste_fournisseurs',
    ]
    
    fieldsets = (
        (_('Informations principales'), {
            'fields': ('nom',)
        }),
        (_('Statistiques'), {
            'fields': ('nombre_fournisseurs_display', 'liste_fournisseurs'),
            'classes': ('collapse',)
        }),
        (_('Informations système'), {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [FournisseurCommoditeInline]
    
    list_per_page = 25
    
    def nombre_fournisseurs_display(self, obj):
        """Affiche le nombre de fournisseurs avec badge"""
        count = obj.nombre_fournisseurs
        if count == 0:
            color = '#dc3545'  # Rouge
        elif count < 5:
            color = '#ffc107'  # Jaune
        else:
            color = '#28a745'  # Vert
        
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 12px; font-weight: bold;">{}</span>',
            color, count
        )
    nombre_fournisseurs_display.short_description = _("Nombre de fournisseurs")
    
    def liste_fournisseurs(self, obj):
        """Affiche la liste des fournisseurs avec leurs villes"""
        liens = obj.liens_fournisseurs.select_related(
            'fournisseur', 
            'fournisseur__ville',
            'fournisseur__ville__zone'
        ).all()
        
        if not liens:
            return format_html('<em style="color: gray;">Aucun fournisseur</em>')
        
        html = '<ul style="margin: 0; padding-left: 20px;">'
        for lien in liens:
            fournisseur = lien.fournisseur
            ville = fournisseur.ville.nom if fournisseur.ville else "Ville inconnue"
            zone = f"Zone {fournisseur.ville.zone.numero}" if fournisseur.ville and fournisseur.ville.zone else ""
            
            html += f'<li><strong>{fournisseur.nom}</strong> - {ville} ({zone})</li>'
        html += '</ul>'
        
        return format_html(html)
    liste_fournisseurs.short_description = _("Liste des fournisseurs")
    
    def nombre_echantillons(self, obj):
        """Compte le nombre d'échantillonnages pour cette commodité"""
        # Cette méthode nécessite que le modèle Echantillonnage ait une relation avec FournisseurCommodite
        return obj.liens_fournisseurs.count()  # À adapter selon votre structure
    nombre_echantillons.short_description = _("Liens fournisseurs")
    
    def get_queryset(self, request):
        """Optimise les requêtes"""
        qs = super().get_queryset(request)
        return qs.prefetch_related(
            'liens_fournisseurs',
            'liens_fournisseurs__fournisseur',
            'liens_fournisseurs__fournisseur__ville',
            'liens_fournisseurs__fournisseur__ville__zone'
        )
    
    class Meta:
        verbose_name = _("Commodité")
        verbose_name_plural = _("Commodités")


@admin.register(FournisseurCommodite)
class FournisseurCommoditeAdmin(SimpleHistoryAdmin):
    """
    Administration du modèle FournisseurCommodite
    """
    list_display = [
        'fournisseur_display',
        'commodite_display',
        'ville_display',
        'zone_display',
        'created_at',
    ]
    
    list_filter = [
        'commodite',
        'fournisseur__ville',
        'fournisseur__ville__zone',
        'created_at',
    ]
    
    search_fields = [
        'fournisseur__nom',
        'commodite__nom',
        'fournisseur__ville__nom',
    ]
    
    readonly_fields = [
        'id',
        'created_at',
        'updated_at',
        'ville_info',
        'zone_info',
    ]
    
    autocomplete_fields = ['fournisseur', 'commodite']
    
    date_hierarchy = 'created_at'
    
    fieldsets = (
        (_('Liaison'), {
            'fields': ('fournisseur', 'commodite')
        }),
        (_('Informations géographiques'), {
            'fields': ('ville_info', 'zone_info'),
            'classes': ('collapse',)
        }),
        (_('Informations système'), {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    list_per_page = 25
    
    def fournisseur_display(self, obj):
        """Affiche le fournisseur"""
        return obj.fournisseur.nom if obj.fournisseur else "-"
    fournisseur_display.short_description = _("Fournisseur")
    fournisseur_display.admin_order_field = 'fournisseur__nom'
    
    def commodite_display(self, obj):
        """Affiche la commodité"""
        return obj.commodite.nom if obj.commodite else "-"
    commodite_display.short_description = _("Commodité")
    commodite_display.admin_order_field = 'commodite__nom'
    
    def ville_display(self, obj):
        """Affiche la ville du fournisseur"""
        return obj.ville.nom if obj.ville else "-"
    ville_display.short_description = _("Ville")
    
    def zone_display(self, obj):
        """Affiche la zone du fournisseur"""
        zone = obj.zone
        return f"Zone {zone.numero}" if zone else "-"
    zone_display.short_description = _("Zone")
    
    def ville_info(self, obj):
        """Affiche les informations détaillées de la ville"""
        ville = obj.ville
        if ville:
            return f"{ville.nom} (Zone {ville.zone.numero})"
        return "-"
    ville_info.short_description = _("Ville (via fournisseur)")
    
    def zone_info(self, obj):
        """Affiche les informations détaillées de la zone"""
        zone = obj.zone
        if zone:
            return f"Zone {zone.numero} - {zone.description or 'Sans description'}"
        return "-"
    zone_info.short_description = _("Zone (via fournisseur)")
    
    def get_queryset(self, request):
        """Optimise les requêtes"""
        qs = super().get_queryset(request)
        return qs.select_related(
            'fournisseur',
            'fournisseur__ville',
            'fournisseur__ville__zone',
            'commodite'
        )
    
    actions = ['exporter_liaisons']
    
    def exporter_liaisons(self, request, queryset):
        """Action pour exporter les liaisons sélectionnées"""
        count = queryset.count()
        self.message_user(
            request,
            f"{count} liaison(s) sélectionnée(s). Fonction d'export à implémenter.",
            level='INFO'
        )
    exporter_liaisons.short_description = _("Exporter les liaisons sélectionnées")
    
    class Meta:
        verbose_name = _("Lien Fournisseur-Commodité")
        verbose_name_plural = _("Liens Fournisseurs-Commodités")