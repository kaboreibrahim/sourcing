from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from simple_history.admin import SimpleHistoryAdmin
from .models import Echantionnage


@admin.register(Echantionnage)
class EchantionnageAdmin(SimpleHistoryAdmin):
    """
    Administration du modèle Echantionnage
    """
    list_display = [
        'reference',
        'fournisseur_display',
        'commodite_display',
        'utilisateur_display',
        'date_creation',
        'prix',
        'quantite',
        'quantite_totale',
        'conformite_display',
        'created_at',
    ]
    
    list_filter = [
        'fournisseur',
        'commodite',
        'utilisateur',
        'date_creation',
        'created_at',
        'updated_at',
    ]
    
    search_fields = [
        'reference',
        'fournisseur__nom',
        'commodite__nom',
        'utilisateur__username',
        'utilisateur__first_name',
        'utilisateur__last_name',
    ]
    
    readonly_fields = [
        'id',
        'reference',
        'created_at',
        'updated_at',
        'commodite_info',
        'fournisseur_info',
        'ville_info',
        'zone_info',
        'conformite_display_detail',
    ]
    
    autocomplete_fields = ['utilisateur']
    
    date_hierarchy = 'date_creation'
    
    fieldsets = (
        (_('Informations générales'), {
            'fields': (
                'reference',
                'fournisseur',
                'commodite',
                'quantite',
                'quantite_totale',
                'prix',
                'date_creation',
            )
        }),
        (_('Analyse qualité'), {
            'fields': (
                'taux_acidite_ffa',
                'impurete_insolubles',
                'teneur_eau_matiere_volatiles_mnl',
            ),
            'classes': ('collapse',)
        }),
        (_('Métadonnées'), {
            'fields': (
                'utilisateur',
                'created_at',
                'updated_at',
            ),
            'classes': ('collapse',)
        }),
        (_('Informations système'), {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    list_per_page = 25
    
    def fournisseur_display(self, obj):
        if obj.fournisseur:
            return f"{obj.fournisseur.nom} ({obj.fournisseur.ville.nom if obj.fournisseur.ville else 'N/A'})"
        return 'Non défini'
    fournisseur_display.short_description = _('Fournisseur')
    
    def commodite_display(self, obj):
        if obj.commodite:
            return format_html(
                '<span style="color: {};">{}</span>',
                obj.commodite.couleur,
                obj.commodite.nom
            )
        return '-'
    commodite_display.short_description = _('Commodité')
    
    def commodite_info(self, obj):
        if hasattr(obj, 'commodite') and obj.commodite:
            return f"{obj.commodite.nom}"
        return "-"
    commodite_info.short_description = _("Commodité")

    
    def utilisateur_display(self, obj):
        """Affiche l'utilisateur (agent)"""
        if obj.utilisateur:
            return f"{obj.utilisateur.get_full_name() or obj.utilisateur.username}"
        return "-"
    utilisateur_display.short_description = _("Agent")
    utilisateur_display.admin_order_field = 'utilisateur__username'
    
    def conformite_display(self, obj):
        """Affiche le statut de conformité avec des couleurs"""
        conformite = obj.est_conforme
        if conformite is None:
            return format_html(
                '<span style="color: gray; font-weight: bold;">⚠ Incomplet</span>'
            )
        elif conformite:
            return format_html(
                '<span style="color: green; font-weight: bold;">✓ Conforme</span>'
            )
        else:
            return format_html(
                '<span style="color: red; font-weight: bold;">✗ Non conforme</span>'
            )
    conformite_display.short_description = _("Conformité")
    
    def conformite_display_detail(self, obj):
        """Affiche les détails de conformité en readonly"""
        conformite = obj.est_conforme
        
        if conformite is None:
            return format_html(
                '<div style="padding: 10px; background-color: #fff3cd; border-left: 4px solid #ffc107;">'
                '<strong style="color: #856404;">⚠ Données incomplètes</strong><br>'
                'Toutes les analyses doivent être renseignées pour évaluer la conformité.'
                '</div>'
            )
        
        details = f"""
        <div style="padding: 10px; background-color: {'#d4edda' if conformite else '#f8d7da'}; 
                    border-left: 4px solid {'#28a745' if conformite else '#dc3545'};">
            <strong style="color: {'#155724' if conformite else '#721c24'};">
                {'✓ Échantillon CONFORME' if conformite else '✗ Échantillon NON CONFORME'}
            </strong><br><br>
            <strong>Critères d'évaluation :</strong><br>
            • Taux d'acidité (FFA) : {obj.taux_acidite_ffa}% 
              {'✓' if obj.taux_acidite_ffa <= 3.0 else '✗ (Max: 3.0%)'}<br>
            • Impuretés insolubles : {obj.impurete_insolubles}% 
              {'✓' if obj.impurete_insolubles <= 0.5 else '✗ (Max: 0.5%)'}<br>
            • Teneur eau/matières volatiles : {obj.teneur_eau_matiere_volatiles_mnl}% 
              {'✓' if obj.teneur_eau_matiere_volatiles_mnl <= 0.2 else '✗ (Max: 0.2%)'}
        </div>
        """
        return format_html(details)
    conformite_display_detail.short_description = _("Détails de conformité")
    
    def fournisseur_info(self, obj):
        """Affiche les informations du fournisseur"""
        fournisseur = obj.fournisseur
        if fournisseur:
            return f"{fournisseur.nom} - {fournisseur.localite or 'Localité non renseignée'}"
        return "-"
    fournisseur_info.short_description = _("Fournisseur (via commodité)")
    
    def ville_info(self, obj):
        """Affiche les informations de la ville"""
        ville = obj.ville
        if ville:
            return f"{ville.nom} (Zone {ville.zone.numero})"
        return "-"
    ville_info.short_description = _("Ville (via fournisseur)")
    
    def zone_info(self, obj):
        """Affiche les informations de la zone"""
        zone = obj.zone
        if zone:
            return f"Zone {zone.numero} - {zone.description or 'Sans description'}"
        return "-"
    zone_info.short_description = _("Zone (via fournisseur)")
    
    
    
    actions = ['marquer_comme_conforme', 'exporter_echantillons']
    
    def marquer_comme_conforme(self, request, queryset):
        """Action personnalisée pour filtrer les échantillons conformes"""
        conformes = [e for e in queryset if e.est_conforme is True]
        self.message_user(
            request,
            f"{len(conformes)} échantillon(s) conforme(s) sur {queryset.count()} sélectionné(s).",
            level='INFO'
        )
    marquer_comme_conforme.short_description = _("Vérifier la conformité des échantillons sélectionnés")
    
    class Meta:
        verbose_name = _("Échantillonnage")
        verbose_name_plural = _("Échantillonnages")