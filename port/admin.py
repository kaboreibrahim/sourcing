from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from .models import Port, FournisseurPort


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


@admin.register(FournisseurPort)
class FournisseurPortAdmin(admin.ModelAdmin):
    """
    Administration du modèle de liaison Fournisseur-Port.
    """
    list_display = ("fournisseur", "port", "created_at", "updated_at")
    list_filter = ("fournisseur", "port")
    search_fields = ("fournisseur__nom", "port__nom")
    ordering = ("fournisseur",)
    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        ("Lien entre le Fournisseur et le Port", {
            "fields": ("fournisseur", "port"),
        }),
        ("Suivi", {
            "fields": ("created_at", "updated_at"),
        }),
    )
