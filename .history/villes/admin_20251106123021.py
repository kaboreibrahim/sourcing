from django.contrib import admin, messages
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from simple_history.admin import SimpleHistoryAdmin

from .models import Ville, Localite, VillePort, PortLocalite


class LocaliteInline(admin.TabularInline):
    """
    Inline pour afficher les localités d'une ville dans l'admin.
    """
    model = Localite
    extra = 0
    fields = ('nom', 'latitude', 'longitude', 'created_at', 'updated_at')
    readonly_fields = ('created_at', 'updated_at')
    show_change_link = True


class VillePortInline(admin.TabularInline):
    """
    Inline pour afficher les ports d'une ville dans l'admin.
    """
    model = VillePort
    extra = 0
    fields = ('port', 'distance', 'created_at', 'updated_at')
    readonly_fields = ('created_at', 'updated_at')
    show_change_link = True


class PortLocaliteInline(admin.TabularInline):
    """
    Inline pour afficher les ports d'une ville dans l'admin.
    """
    model = PortLocalite
    extra = 0
    fields = ('port', 'distance', 'created_at', 'updated_at')
    readonly_fields = ('created_at', 'updated_at')
    show_change_link = True


@admin.register(Ville)
class VilleAdmin(SimpleHistoryAdmin):
    """
    Administration du modèle Ville
    """
    list_display = [
        'nom',
        'zone_display',
        'est_ville_reference_display',
        'superficie',
        'latitude',
        'longitude',
        'created_at',
        'updated_at',
    ]
    
    list_filter = [
        'zone',
        'est_ville_reference',
        'created_at',
        'updated_at',
    ]
    
    search_fields = [
        'nom',
        'description',
        'zone__numero',
    ]
    
    readonly_fields = [
        'id',
        'created_at',
        'updated_at',
    ]
    
    autocomplete_fields = ['zone']
    inlines = [LocaliteInline,VillePortInline,PortLocaliteInline]
    list_per_page = 25
    
    fieldsets = (
        (_('Informations principales'), {
            'fields': ('nom', 'zone', 'est_ville_reference', 'description')
        }),
        (_('Superficie'), {
            'fields': ('superficie','latitude','longitude')
        }),
        (_('Informations système'), {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def zone_display(self, obj):
        """Affiche la zone avec un lien"""
        return f"Zone {obj.zone.numero}"
    zone_display.short_description = _("Zone")
    zone_display.admin_order_field = 'zone__numero'
    
    def est_ville_reference_display(self, obj):
        """Affiche le statut de ville de référence avec une icône"""
        if obj.est_ville_reference:
            return format_html(
                '<span style="color: gold; font-size: 18px;">⭐</span> '
                '<span style="color: green; font-weight: bold;">Oui</span>'
            )
        return format_html('<span style="color: gray;">Non</span>')
    est_ville_reference_display.short_description = _("Ville de référence")
    est_ville_reference_display.admin_order_field = 'est_ville_reference'
    
    def save_model(self, request, obj, form, change):
        """
        Surcharge pour afficher un message si la ville devient ville de référence
        """
        was_reference = False
        if change:
            old_obj = Ville.objects.get(pk=obj.pk)
            was_reference = old_obj.est_ville_reference
        
        super().save_model(request, obj, form, change)
        
        if obj.est_ville_reference and not was_reference:
            self.message_user(
                request,
                _(f"'{obj.nom}' est maintenant la ville de référence de la Zone {obj.zone.numero}."),
                level=messages.SUCCESS
            )


@admin.register(Localite)
class LocaliteAdmin(SimpleHistoryAdmin):
    """
    Administration du modèle Localite
    """
    list_display = [
        'nom',
        'ville_display',
        'latitude',
        'longitude',
        'created_at',
    ]
    
    list_filter = ['ville', 'created_at', 'updated_at']
    search_fields = ['nom', 'ville__nom']
    readonly_fields = ['id', 'created_at', 'updated_at']
    autocomplete_fields = ['ville']
    list_per_page = 25
    
    fieldsets = (
        (_('Informations principales'), {
            'fields': ('nom', 'ville')
        }),
        (_('Superficie'), {
            'fields': ('latitude','longitude')
        }),
        (_('Informations système'), {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def ville_display(self, obj):
        return obj.ville.nom
    ville_display.short_description = _("Ville")
    ville_display.admin_order_field = 'ville__nom'
