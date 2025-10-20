from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from simple_history.admin import SimpleHistoryAdmin
from .models import Ville


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
        'distance_port_abidjan',
        'distance_port_sanpedro',
        'created_at',
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
    
    fieldsets = (
        (_('Informations principales'), {
            'fields': ('nom', 'zone', 'est_ville_reference', 'description')
        }),
        (_('Superficie et localisation'), {
            'fields': ('superficie', 'distance_port_abidjan', 'distance_port_sanpedro')
        }),
        (_('Informations système'), {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    list_per_page = 25
    
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
                f"'{obj.nom}' est maintenant la ville de référence de la Zone {obj.zone.numero}",
                level='SUCCESS'
            )
    
    class Meta:
        verbose_name = _("Ville")
        verbose_name_plural = _("Villes")