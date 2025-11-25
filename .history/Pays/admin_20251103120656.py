from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from safedelete.admin import SafeDeleteAdmin, highlight_deleted
from .models import Pays





@admin.register(Pays)
class PaysAdmin(SimpleHistoryAdmin,SafeDeleteAdmin):

    """
    interface d'administration pour le pays
    """
    
    list_display = (
        'nom',
        'code',
        'created_at',
        'updated_at',
        highlight_deleted,
    )
    
    search_fields = ('nom', 'code')
    list_filter = (
        'created_at',
        'updated_at',
        'deleted',
    )
    readonly_fields = (
        'id',
        'created_at',
        'updated_at',
    )
    fieldsets = (
        (_('Informations principales'), {
            'fields': ('id', 'nom', 'code')
        }),
        (_('Dates'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
    ordering = ('nom',)
    list_per_page = 25