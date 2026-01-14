from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from simple_history.admin import SimpleHistoryAdmin
from .models import Fournisseur
from commodites.models import FournisseurCommodite
from django.urls import reverse
from django.utils.html import format_html
from django.contrib.auth import get_user_model


class FournisseurCommoditeInline(admin.TabularInline):
    """
    Inline pour gérer les commodités d'un fournisseur
    """
    model = FournisseurCommodite
    fk_name = 'fournisseur'
    extra = 1
    autocomplete_fields = ['commodite']
    readonly_fields = ['created_at']
    
    fields = ['commodite', 'created_at']
    
    verbose_name = _("Commodité")
    verbose_name_plural = _("Commodités fournies")


class FournisseurAdminForm(forms.ModelForm):
    class Meta:
        model = Fournisseur
        fields = '__all__'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Si un utilisateur est déjà lié, limiter les choix à cet utilisateur
        if self.instance and self.instance.user:
            self.fields['user'].queryset = get_user_model().objects.filter(pk=self.instance.user.pk)
        else:
            # Sinon, ne montrer que les utilisateurs de type fournisseur sans fournisseur lié
            self.fields['user'].queryset = get_user_model().objects.filter(
                type_user='FS',
                fournisseur_profile__isnull=True
            )

@admin.register(Fournisseur)
class FournisseurAdmin(SimpleHistoryAdmin):
    """
    Administration du modèle Fournisseur
    """

    def user_link(self, obj):
        if obj.user:
            url = reverse('admin:utilisateur_utilisateur_change', args=[obj.user.id])
            return format_html('<a href="{}">{}</a>', url, obj.user.username)
        return "-"
    user_link.short_description = "Compte utilisateur"
    user_link.allow_tags = True

    list_display = [
        'nom',
        'nom_responsable',
        'ville_display',
        'zone_display',
        'contact',
        'localite',
        'has_document',
        'user_link',  # Remplacer has_user_account par user_link
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
        (None, {
            'fields': ('nom', 'nom_responsable', 'contact', 'ville', 'localite')
        }),
        ('Localisation géographique', {
            'fields': ('latitude', 'longitude')
        }),
        ('Documents', {
            'fields': ('document_fourni_aex',)
        }),
        ('Compte utilisateur', {
            'fields': ('user',),
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

     # Ajout de la méthode pour afficher si un compte utilisateur est lié
    def has_user_account(self, obj):
        return obj.user is not None
    has_user_account.boolean = True
    has_user_account.short_description = 'Compte utilisateur'
        
    
    class Meta:
        verbose_name = _("Fournisseur")
        verbose_name_plural = _("Fournisseurs")

# # Dans fournisseurs/admin.py
# @admin.register(Fournisseur)
# class FournisseurAdmin(admin.ModelAdmin):
#     list_display = ('nom', 'ville', 'contact', 'a_un_utilisateur')
    
#     def a_un_utilisateur(self, obj):
#         return obj.user is not None
#     a_un_utilisateur.boolean = True
#     a_un_utilisateur.short_description = 'A un utilisateur'