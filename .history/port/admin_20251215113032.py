from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from .models import Port


@admin.register(Port)
class PortAdmin(SimpleHistoryAdmin):
    """
    Administration du modèle Port.
    """
    list_display = ("nom", "pays", "latitude", "longitude", "created_at", "updated_at")
    list_filter = ("pays",)
    search_fields = ("nom", "pays__nom")
    ordering = ("nom",)
    readonly_fields = ("created_at", "updated_at")
    history_list_display = ["nom", "pays"]

    fieldsets = (
        ("Informations sur le port", {
            "fields": ("nom", "pays", "latitude", "longitude")
        }),
        ("Suivi", {
            "fields": ("created_at", "updated_at"),
        }),
    )
 