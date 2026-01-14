from django.contrib import admin
from .models import DemandeCotation


@admin.register(DemandeCotation)
class DemandeCotationAdmin(admin.ModelAdmin):
    list_display = (
        'ref',
        'nom_client',
        'commodite',
        'quantite',
        'incoterm',
        'pol',
        'pod',
        'statut',
        'date_demande',
    )

    list_filter = (
        'statut',
        'incoterm',
        'type_conditionnement',
        'date_demande',
    )

    search_fields = (
        'nom_client',
        'contact',
        'pol',
        'pod',
    )

    readonly_fields = ('date_demande',)

    ordering = ('-date_demande',)

    fieldsets = (
        ('Informations client', {
            'fields': ('nom_client', 'contact')
        }),
        ('Détails de la cotation', {
            'fields': (
                'commodite',
                'quantite',
                'type_conditionnement',
                'incoterm',
                'target_price',
            )
        }),
        ('Logistique', {
            'fields': ('pol', 'pod')
        }),
        ('Statut', {
            'fields': ('statut',)
        }),
        ('Informations système', {
            'fields': ('date_demande',)
        }),
    )
