from django.db import models
from django.utils.translation import gettext_lazy as _
from commodites.models import Commodite
import datetime
import uuid


class DemandeCotation(models.Model):


    id = models.UUIDField(
            _("Identifiant unique"),
            primary_key=True,
            default=uuid.uuid4,
            editable=False
        )

        
    INCOTERMS_CHOICES = [
        ('EXW', _('EXW')),
        ('FOB', _('FOB')),
        ('CIF', _('CIF')),
        ('CFR', _('CFR')),
    ]

    CONDITIONNEMENT_CHOICES = [
        ('VRAC', _('Vrac')),
        ('FLEXITANK', _('Flexitank')),
        ('ISOTANK', _('Isotank')),
        ('AUTRE', _('Autre')),
    ]

    STATUT_CHOICES = [
        ('EN_ATTENTE', _('En attente')),
        ('TRAITEE', _('Traitée')),
        ('REFUSEE', _('Refusée')),
    ]

    nom_client = models.CharField(_("Nom client"), max_length=255)
    contact = models.CharField(_("Contact"), max_length=50)

    mail = models.EmailField(_("Email"), null=True, blank=True)

    commodite = models.ForeignKey(Commodite, on_delete=models.CASCADE, verbose_name=_("Commodité"))

    quantite = models.DecimalField(_("Quantité"), max_digits=10, decimal_places=2)

    type_conditionnement = models.CharField(
        _("Type de conditionnement"),
        max_length=20,
        choices=CONDITIONNEMENT_CHOICES,
        default='CONTENEUR'
    )

    incoterm = models.CharField(
        _("Incoterm"),
        max_length=10,
        choices=INCOTERMS_CHOICES,
        default='FOB'
    )

    pol = models.CharField(
        _("Port de chargement (POL)"),
        max_length=255,
        choices=[
            ('ABIDJ', _('Abidjan')),
            ('SAN', _('San Pedro')),
        ]
    )
    pod = models.CharField(_("Port de déchargement (POD)"), max_length=255)

    target_price = models.DecimalField(_("Prix cible"), max_digits=10, decimal_places=2)
    target_price_currency = models.CharField(
        _("Devise du prix cible"),
        max_length=3,
        choices=[
            ('XOF', _('XOF (Francs CFA)')),
            ('USD', _('USD (Dollars)')),
            ('EUR', _('EUR (Euros)')),
            ('GBP', _('GBP (Livres sterling)')),
            ('CHF', _('CHF (Francs suisses)')),
        ]
    )

    statut = models.CharField(
        _("Statut"),
        max_length=20,
        choices=STATUT_CHOICES,
        default='EN_ATTENTE'
    )

    date_demande = models.DateTimeField(_("Date de demande"), auto_now_add=True)

    @property
    def ref(self):
        """
        Génère une référence unique en utilisant le format: REF-YYMMDDHHMMSS-<id>
        Cette propriété est accessible après la sauvegarde de l'objet (quand id existe)
        """
        if self.id:
            now = self.date_demande.strftime("%y%m%d%H%M%S")
            return f"REF-{now}"
        return _("REF-PENDING")

    def __str__(self):
        return f"{self.nom_client} - {self.commodite} ({self.get_statut_display()})"

    class Meta:
        verbose_name = _("Demande de cotation")
        verbose_name_plural = _("Demandes de cotation")
        ordering = ['-date_demande']


class EmailQueue(models.Model):
    """
    File d'attente pour les emails à envoyer
    Permet l'envoi différé via cron au lieu de Celery
    """
    
    EMAIL_TYPE_CHOICES = [
        ('CLIENT_CONFIRMATION', _('Confirmation client')),
        ('ADMIN_NOTIFICATION', _('Notification admin')),
    ]
    
    demande = models.ForeignKey(
        DemandeCotation,
        on_delete=models.CASCADE,
        related_name='emails',
        verbose_name=_("Demande")
    )
    
    email_type = models.CharField(
        _("Type d'email"),
        max_length=50,
        choices=EMAIL_TYPE_CHOICES
    )
    
    to_email = models.EmailField(_("Email destinataire"))
    cc_emails = models.TextField(blank=True, help_text=_("Emails en copie, séparés par des virgules"))
    subject = models.CharField(_("Sujet"), max_length=255)
    html_content = models.TextField(_("Contenu HTML"))
    text_content = models.TextField(_("Contenu texte"), blank=True)
    
    created_at = models.DateTimeField(_("Date de création"), auto_now_add=True)
    sent = models.BooleanField(_("Envoyé"), default=False)
    sent_at = models.DateTimeField(_("Date d'envoi"), null=True, blank=True)
    
    attempts = models.IntegerField(_("Tentatives"), default=0)
    error_message = models.TextField(_("Message d'erreur"), blank=True)
    
    class Meta:
        verbose_name = _("Email en attente")
        verbose_name_plural = _("Emails en attente")
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['sent', 'created_at']),
            models.Index(fields=['demande']),
        ]
    
    def __str__(self):
        status = _("✓ Envoyé") if self.sent else _("⏳ En attente")
        return f"{status} - {self.email_type} pour {self.demande.ref}"