from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from simple_history.admin import SimpleHistoryAdmin
from .models import Fournisseur
from commodite.models import FournisseurCommodite


class FournisseurCommoditeInline(admin.TabularInline):
    """
    Inline pour gérer les commodités d'un fournisseur
    """
    model = None  # Sera défini dynamiquement
    fk_name = 'fournisseur'
    extra = 1
    autocomplete_fields = ['commodite']
    readonly_fields = ['created_at']
    
    fields = ['commodite', 'created_at']
    
    verbose_name = _("Commodité")
    verbose_name_plural = _("Commodités fournies")
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Import dynamique pour éviter les imports circulaires
        from commodite.models import FournisseurCommodite
        self.model = FournisseurCommodite


@admin.register(Fournisseur)
class FournisseurAdmin(SimpleHistoryAdmin):
    """
    Administration du modèle Fournisseur
    """
    list_display = [
        'nom',
        'nom_responsable',
        'ville_display',
        'zone_display',
        'contact',
        'localite',
        'nombre_commodites_display',
        'has_document',
        'created_at',
    ]
    
    list_filter = [
        'ville',
        'ville__zone',
        'created_at',
        'updated_at',
    ]
    
    search_fields = [
        'nom',
        'nom_responsable',
        'contact',
        'localite',
        'ville__nom',
    ]
    
    readonly_fields = [
        'id',
        'created_at',
        'updated_at',
        'zone_info',
        'nombre_commodites_display',
        'liste_commodites',
    ]
    
    autocomplete_fields = ['ville']
    
    fieldsets = (
        (_('Informations principales'), {
            'fields': ('nom', 'nom_responsable', 'contact', 'ville', 'localite')
        }),
        (_('Localisation géographique'), {
            'fields': ('latitude', 'longitude', 'zone_info')
        }),
        (_('Distances aux ports'), {
            'fields': ('distance_port_abidjan', 'distance_port_sanpedro'),
            'classes': ('collapse',)
        }),
        (_('Documents'), {
            'fields': ('document_fourni_aex',)
        }),
        (_('Commodités'), {
            'fields': ('nombre_commodites_display', 'liste_commodites'),
            'classes': ('collapse',)
        }),
        (_('Informations système'), {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [FournisseurCommoditeInline]
    
    list_per_page = 25
    
    def ville_display(self, obj):
        """Affiche la ville"""
        return obj.ville.nom if obj.ville else "-"
    ville_display.short_description = _("Ville")
    ville_display.admin_order_field = 'ville__nom'
    
    def zone_display(self, obj):
        """Affiche la zone via la ville"""
        if obj.ville and obj.ville.zone:
            return f"Zone {obj.ville.zone.numero}"
        return "-"
    zone_display.short_description = _("Zone")
    zone_display.admin_order_field = 'ville__zone__numero'
    
    def zone_info(self, obj):
        """Affiche les informations de la zone en readonly"""
        zone = obj.get_zone
        if zone:
            return f"Zone {zone.numero} - {zone.description or 'Sans description'}"
        return "-"
    zone_info.short_description = _("Zone (via ville)")
    
    def has_document(self, obj):
        """Indique si le fournisseur a uploadé un document"""
        if obj.document_fourni_aex:
            return format_html(
                '<span style="color: green;">✓</span> '
                '<a href="{}" target="_blank">Voir</a>',
                obj.document_fourni_aex.url
            )
        return format_html('<span style="color: red;">✗</span>')
    has_document.short_description = _("Document")
    
    def nombre_commodites_display(self, obj):
        """Affiche le nombre de commodités avec badge"""
        count = obj.nombre_commodites
        if count == 0:
            color = '#dc3545'  # Rouge
        elif count < 3:
            color = '#ffc107'  # Jaune
        else:
            color = '#28a745'  # Vert
        
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 12px; font-weight: bold;">{}</span>',
            color, count
        )
    nombre_commodites_display.short_description = _("Commodités")
    
    def liste_commodites(self, obj):
        """Affiche la liste des commodités fournies"""
        liens = obj.liens_commodites.select_related('commodite').all()
        
        if not liens:
            return format_html('<em style="color: gray;">Aucune commodité</em>')
        
        html = '<ul style="margin: 0; padding-left: 20px;">'
        for lien in liens:
            html += f'<li><strong>{lien.commodite.nom}</strong></li>'
        html += '</ul>'
        
        return format_html(html)
    liste_commodites.short_description = _("Liste des commodités")
    
    def get_queryset(self, request):
        """Optimise les requêtes avec select_related"""
        qs = super().get_queryset(request)
        return qs.select_related('ville', 'ville__zone').prefetch_related(
            'liens_commodites',
            'liens_commodites__commodite'
        )
    
    class Meta:
        verbose_name = _("Fournisseur")
        verbose_name_plural = _("Fournisseurs")