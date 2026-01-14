# admin.py
from django.contrib import admin
from django.utils.html import format_html
from .models import DemandeCotation, EmailQueue


@admin.register(DemandeCotation)
class DemandeCotationAdmin(admin.ModelAdmin):
    list_display = [
        'ref', 'nom_client','mail', 'commodite', 'quantite', 
        'statut_badge', 'date_demande'
    ]
    list_filter = ['statut', 'commodite', 'date_demande']
    search_fields = ['nom_client', 'contact', 'commodite__nom']
    readonly_fields = ['date_demande']
    
    fieldsets = (
        ('Informations client', {
            'fields': ('nom_client', 'contact')
        }),
        ('Détails de la demande', {
            'fields': (
                'commodite', 'quantite', 'type_conditionnement',
                'incoterm', 'pol', 'pod', 'target_price'
            )
        }),
        ('Statut', {
            'fields': ('statut', 'date_demande')
        }),
    )
    
    def statut_badge(self, obj):
        colors = {
            'EN_ATTENTE': 'orange',
            'TRAITEE': 'green',
            'REFUSEE': 'red',
        }
        color = colors.get(obj.statut, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 3px;">{}</span>',
            color,
            obj.get_statut_display()
        )
    statut_badge.short_description = 'Statut'


@admin.register(EmailQueue)
class EmailQueueAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'email_type_badge', 'to_email', 'demande_ref',
        'sent_badge', 'attempts', 'created_at'
    ]
    list_filter = ['sent', 'email_type', 'created_at']
    search_fields = ['to_email', 'subject', 'demande__nom_client']
    readonly_fields = ['created_at', 'sent_at', 'html_content_preview']
    
    fieldsets = (
        ('Informations', {
            'fields': ('demande', 'email_type', 'to_email', 'subject')
        }),
        ('Contenu', {
            'fields': ('html_content_preview', 'text_content'),
            'classes': ('collapse',)
        }),
        ('Statut d\'envoi', {
            'fields': ('sent', 'sent_at', 'attempts', 'error_message')
        }),
        ('Dates', {
            'fields': ('created_at',)
        }),
    )
    
    actions = ['resend_emails', 'mark_as_sent', 'delete_sent_emails']
    
    def email_type_badge(self, obj):
        colors = {
            'CLIENT_CONFIRMATION': '#007bff',
            'ADMIN_NOTIFICATION': '#17a2b8',
        }
        color = colors.get(obj.email_type, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; '
            'border-radius: 3px; font-size: 11px;">{}</span>',
            color,
            obj.get_email_type_display()
        )
    email_type_badge.short_description = 'Type'
    
    def sent_badge(self, obj):
        if obj.sent:
            return format_html(
                '<span style="background-color: green; color: white; padding: 3px 10px; '
                'border-radius: 3px;">✓ Envoyé</span>'
            )
        elif obj.attempts >= 3:
            return format_html(
                '<span style="background-color: red; color: white; padding: 3px 10px; '
                'border-radius: 3px;">✗ Échec</span>'
            )
        else:
            return format_html(
                '<span style="background-color: orange; color: white; padding: 3px 10px; '
                'border-radius: 3px;">⏳ En attente</span>'
            )
    sent_badge.short_description = 'Statut'
    
    def demande_ref(self, obj):
        return obj.demande.ref
    demande_ref.short_description = 'Référence demande'
    
    def html_content_preview(self, obj):
        if obj.html_content:
            return format_html(
                '<div style="max-height: 300px; overflow-y: auto; border: 1px solid #ddd; '
                'padding: 10px; background: #f9f9f9;">{}</div>',
                obj.html_content
            )
        return "Pas de contenu HTML"
    html_content_preview.short_description = 'Aperçu HTML'
    
    def resend_emails(self, request, queryset):
        """Réinitialiser les emails sélectionnés pour un nouvel envoi"""
        count = queryset.update(sent=False, attempts=0, error_message='')
        self.message_user(
            request, 
            f'{count} email(s) réinitialisé(s) pour un nouvel envoi.'
        )
    resend_emails.short_description = "Réinitialiser pour renvoyer"
    
    def mark_as_sent(self, request, queryset):
        """Marquer comme envoyé (pour les tests)"""
        from django.utils import timezone
        count = queryset.update(sent=True, sent_at=timezone.now())
        self.message_user(request, f'{count} email(s) marqué(s) comme envoyé(s).')
    mark_as_sent.short_description = "Marquer comme envoyé"
    
    def delete_sent_emails(self, request, queryset):
        """Supprimer uniquement les emails envoyés"""
        sent_emails = queryset.filter(sent=True)
        count = sent_emails.count()
        sent_emails.delete()
        self.message_user(
            request, 
            f'{count} email(s) envoyé(s) supprimé(s).'
        )
    delete_sent_emails.short_description = "Supprimer les emails envoyés"