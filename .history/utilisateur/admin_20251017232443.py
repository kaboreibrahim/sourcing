from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from simple_history.admin import SimpleHistoryAdmin
from .models import Utilisateur, CodeVerification


@admin.register(Utilisateur)
class UtilisateurAdmin(UserAdmin, SimpleHistoryAdmin):
    """
    Administration du modèle Utilisateur personnalisé
    """
    list_display = [
        'username',
        'email',
        'full_name',
        'type_user_display',
        'is_online_display',
        'is_verified_display',
        'phone',
        'last_login',
        'date_joined',
    ]
    
    list_filter = [
        'type_user',
        'is_staff',
        'is_superuser',
        'is_active',
        'is_verified',
        'is_online',
        'two_factor_method',
        'date_joined',
        'last_login',
    ]
    
    search_fields = [
        'username',
        'first_name',
        'last_name',
        'email',
        'phone',
    ]
    
    readonly_fields = [
        'id',
        'date_joined',
        'last_login',
        'is_online',
        'google_auth_secret',
    ]
    
    fieldsets = (
        (_('Informations de connexion'), {
            'fields': ('username', 'password', 'email')
        }),
        (_('Informations personnelles'), {
            'fields': (
                'first_name',
                'last_name',
                'phone',
                'photo_profil',
                'type_user'
            )
        }),
        (_('Authentification à deux facteurs'), {
            'fields': ('two_factor_method', 'google_auth_secret'),
            'classes': ('collapse',)
        }),
        (_('Permissions'), {
            'fields': (
                'is_active',
                'is_verified',
                'is_staff',
                'is_superuser',
                'groups',
                'user_permissions'
            )
        }),
        (_('Informations de connexion'), {
            'fields': ('is_online', 'last_login', 'date_joined'),
            'classes': ('collapse',)
        }),
        (_('Identifiant système'), {
            'fields': ('id',),
            'classes': ('collapse',)
        }),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'username',
                'email',
                'password1',
                'password2',
                'first_name',
                'last_name',
                'phone',
                'type_user',
                'is_staff',
                'is_superuser'
            ),
        }),
    )
    
    list_per_page = 25
    
    def full_name(self, obj):
        """Affiche le nom complet de l'utilisateur"""
        return obj.get_full_name() or "-"
    full_name.short_description = _("Nom complet")
    full_name.admin_order_field = 'first_name'
    
    def type_user_display(self, obj):
        """Affiche le type d'utilisateur avec des couleurs"""
        type_colors = {
            'AS': '#007bff',  # Bleu pour Agent Sourcing
            'AO': '#28a745',  # Vert pour Agent Opérationnel
        }
        color = type_colors.get(obj.type_user, '#6c757d')
        label = obj.get_type_user_display()
        
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 3px; font-weight: bold;">{}</span>',
            color, label
        )
    type_user_display.short_description = _("Type d'utilisateur")
    type_user_display.admin_order_field = 'type_user'
    
    def is_online_display(self, obj):
        """Affiche le statut en ligne avec une icône"""
        if obj.is_online:
            return format_html(
                '<span style="color: green; font-size: 16px;" title="En ligne">●</span>'
            )
        return format_html(
            '<span style="color: gray; font-size: 16px;" title="Hors ligne">●</span>'
        )
    is_online_display.short_description = _("En ligne")
    is_online_display.admin_order_field = 'is_online'
    
    def is_verified_display(self, obj):
        """Affiche le statut de vérification avec une icône"""
        if obj.is_verified:
            return format_html(
                '<span style="color: green; font-weight: bold;">✓</span>'
            )
        return format_html(
            '<span style="color: red; font-weight: bold;">✗</span>'
        )
    is_verified_display.short_description = _("Vérifié")
    is_verified_display.admin_order_field = 'is_verified'
    
    def get_queryset(self, request):
        """Optimise les requêtes"""
        qs = super().get_queryset(request)
        return qs.select_related().prefetch_related('groups', 'user_permissions')
    
    actions = ['activer_utilisateurs', 'desactiver_utilisateurs', 'verifier_utilisateurs']
    
    def activer_utilisateurs(self, request, queryset):
        """Action pour activer les utilisateurs sélectionnés"""
        updated = queryset.update(is_active=True)
        self.message_user(
            request,
            f"{updated} utilisateur(s) activé(s) avec succès.",
            level='SUCCESS'
        )
    activer_utilisateurs.short_description = _("Activer les utilisateurs sélectionnés")
    
    def desactiver_utilisateurs(self, request, queryset):
        """Action pour désactiver les utilisateurs sélectionnés"""
        updated = queryset.update(is_active=False)
        self.message_user(
            request,
            f"{updated} utilisateur(s) désactivé(s) avec succès.",
            level='WARNING'
        )
    desactiver_utilisateurs.short_description = _("Désactiver les utilisateurs sélectionnés")
    
    def verifier_utilisateurs(self, request, queryset):
        """Action pour vérifier les utilisateurs sélectionnés"""
        updated = queryset.update(is_verified=True)
        self.message_user(
            request,
            f"{updated} utilisateur(s) vérifié(s) avec succès.",
            level='SUCCESS'
        )
    verifier_utilisateurs.short_description = _("Vérifier les utilisateurs sélectionnés")
    
    class Meta:
        verbose_name = _("Utilisateur")
        verbose_name_plural = _("Utilisateurs")


@admin.register(CodeVerification)
class CodeVerificationAdmin(SimpleHistoryAdmin):
    """
    Administration du modèle CodeVerification
    """
    list_display = [
        'code',
        'user_display',
        'type_code_display',
        'email',
        'is_used_display',
        'attempts_display',
        'expires_at',
        'created_at',
    ]
    
    list_filter = [
        'type_code',
        'is_used',
        'created_at',
        'expires_at',
    ]
    
    search_fields = [
        'code',
        'user__username',
        'user__email',
        'email',
    ]
    
    readonly_fields = [
        'id',
        'code',
        'user',
        'type_code',
        'email',
        'created_at',
        'used_at',
        'is_expired_display',
        'is_valid_display',
    ]
    
    fieldsets = (
        (_('Informations du code'), {
            'fields': ('id', 'code', 'user', 'type_code', 'email')
        }),
        (_('Statut'), {
            'fields': (
                'is_used',
                'is_expired_display',
                'is_valid_display',
                'attempts',
                'max_attempts'
            )
        }),
        (_('Dates'), {
            'fields': ('created_at', 'expires_at', 'used_at'),
            'classes': ('collapse',)
        }),
    )
    
    list_per_page = 25
    date_hierarchy = 'created_at'
    
    def has_add_permission(self, request):
        """Empêche l'ajout manuel de codes de vérification"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Empêche la modification des codes de vérification"""
        return False
    
    def user_display(self, obj):
        """Affiche l'utilisateur"""
        if obj.user:
            return f"{obj.user.username} ({obj.user.get_full_name() or 'Sans nom'})"
        return "-"
    user_display.short_description = _("Utilisateur")
    user_display.admin_order_field = 'user__username'
    
    def type_code_display(self, obj):
        """Affiche le type de code avec des couleurs"""
        type_colors = {
            'activation': '#17a2b8',      # Info (cyan)
            'otp': '#ffc107',             # Warning (jaune)
            'password_reset': '#dc3545',  # Danger (rouge)
            'email_change': '#6f42c1',    # Purple
        }
        color = type_colors.get(obj.type_code, '#6c757d')
        label = obj.get_type_code_display()
        
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 3px; font-size: 11px; font-weight: bold;">{}</span>',
            color, label
        )
    type_code_display.short_description = _("Type de code")
    type_code_display.admin_order_field = 'type_code'
    
    def is_used_display(self, obj):
        """Affiche si le code a été utilisé"""
        if obj.is_used:
            return format_html(
                '<span style="color: green; font-weight: bold;">✓ Utilisé</span>'
            )
        return format_html(
            '<span style="color: orange; font-weight: bold;">⏳ En attente</span>'
        )
    is_used_display.short_description = _("Utilisé")
    is_used_display.admin_order_field = 'is_used'
    
    def attempts_display(self, obj):
        """Affiche le nombre de tentatives avec une barre de progression"""
        percentage = (obj.attempts / obj.max_attempts) * 100
        
        if obj.attempts >= obj.max_attempts:
            color = '#dc3545'  # Rouge
            status = 'Bloqué'
        elif obj.attempts > 0:
            color = '#ffc107'  # Jaune
            status = f'{obj.attempts}/{obj.max_attempts}'
        else:
            color = '#28a745'  # Vert
            status = f'{obj.attempts}/{obj.max_attempts}'
        
        return format_html(
            '<div style="width: 100px;">'
            '<div style="background-color: #e9ecef; border-radius: 4px; overflow: hidden;">'
            '<div style="background-color: {}; width: {}%; height: 20px; '
            'display: flex; align-items: center; justify-content: center; '
            'color: white; font-size: 11px; font-weight: bold;">{}</div>'
            '</div></div>',
            color, percentage, status
        )
    attempts_display.short_description = _("Tentatives")
    
    def is_expired_display(self, obj):
        """Affiche si le code a expiré"""
        if obj.is_expired():
            return format_html(
                '<span style="color: red; font-weight: bold;">✗ Expiré</span>'
            )
        return format_html(
            '<span style="color: green; font-weight: bold;">✓ Valide</span>'
        )
    is_expired_display.short_description = _("Expiration")
    
    def is_valid_display(self, obj):
        """Affiche si le code est valide (statut global)"""
        if obj.is_valid():
            return format_html(
                '<div style="padding: 5px 10px; background-color: #d4edda; '
                'border-left: 3px solid #28a745; color: #155724;">'
                '<strong>✓ Code valide</strong><br>'
                '<small>Peut être utilisé</small>'
                '</div>'
            )
        else:
            reasons = []
            if obj.is_used:
                reasons.append("Déjà utilisé")
            if obj.is_expired():
                reasons.append("Expiré")
            if obj.attempts >= obj.max_attempts:
                reasons.append("Tentatives épuisées")
            
            return format_html(
                '<div style="padding: 5px 10px; background-color: #f8d7da; '
                'border-left: 3px solid #dc3545; color: #721c24;">'
                '<strong>✗ Code invalide</strong><br>'
                '<small>{}</small>'
                '</div>',
                " | ".join(reasons)
            )
    is_valid_display.short_description = _("Statut global")
    
    def get_queryset(self, request):
        """Optimise les requêtes"""
        qs = super().get_queryset(request)
        return qs.select_related('user')
    
    actions = ['marquer_comme_utilise', 'supprimer_codes_expires']
    
    def marquer_comme_utilise(self, request, queryset):
        """Action pour marquer les codes comme utilisés"""
        updated = 0
        for code in queryset:
            if not code.is_used:
                code.mark_as_used()
                updated += 1
        
        self.message_user(
            request,
            f"{updated} code(s) marqué(s) comme utilisé(s).",
            level='SUCCESS'
        )
    marquer_comme_utilise.short_description = _("Marquer comme utilisé")
    
    def supprimer_codes_expires(self, request, queryset):
        """Action pour supprimer les codes expirés"""
        codes_expires = [code for code in queryset if code.is_expired()]
        count = len(codes_expires)
        
        for code in codes_expires:
            code.delete()
        
        self.message_user(
            request,
            f"{count} code(s) expiré(s) supprimé(s).",
            level='WARNING'
        )
    supprimer_codes_expires.short_description = _("Supprimer les codes expirés")
    
    class Meta:
        verbose_name = _("Code de vérification")
        verbose_name_plural = _("Codes de vérification")