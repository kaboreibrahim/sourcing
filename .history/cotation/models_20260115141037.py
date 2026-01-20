from django.db import models
from commodites.models import Commodite
import datetime
import uuid


class DemandeCotation(models.Model):


    id = models.UUIDField(
            "Identifiant unique",
            primary_key=True,
            default=uuid.uuid4,
            editable=False
        )

        
    INCOTERMS_CHOICES = [
        ('EXW', 'EXW'),
        ('FOB', 'FOB'),
        ('CIF', 'CIF'),
        ('CFR', 'CFR'),
    ]

    CONDITIONNEMENT_CHOICES = [
        ('VRAC', 'Vrac'),
        ('FLEXITANK', 'Flexitank'),
        ('ISOTANK', 'Isotank'),
        ('AUTRE', 'Autre'),
    ]

    STATUT_CHOICES = [
        ('EN_ATTENTE', 'En attente'),
        ('TRAITEE', 'Traitée'),
        ('REFUSEE', 'Refusée'),
    ]

    nom_client = models.CharField(max_length=255)
    contact = models.CharField(max_length=50)

    mail = models.EmailField(null=True, blank=True)

    commodite = models.ForeignKey(Commodite, on_delete=models.CASCADE)

    quantite = models.DecimalField(max_digits=10, decimal_places=2)

    type_conditionnement = models.CharField(
        max_length=20,
        choices=CONDITIONNEMENT_CHOICES,
        default='CONTENEUR'
    )

    incoterm = models.CharField(
        max_length=10,
        choices=INCOTERMS_CHOICES,
        default='FOB'
    )

    pol = models.CharField(
        "Port de chargement (POL)",
        max_length=255,
        blank=True,
        choices=[
            ('ABIDJ', 'Abidjan'),
            ('SAN', 'San Pedro'),
        ]
    )
    pod = models.CharField("Port de déchargement (POD)", max_length=255, blank=True)

    target_price = models.DecimalField(max_digits=10, decimal_places=2)
    target_price_currency = models.CharField(
        max_length=3,
        choices=[
            ('XOF', 'XOF (Francs CFA)'),
            ('USD', 'USD (Dollars)'),
            ('EUR', 'EUR (Euros)'),
            ('GBP', 'GBP (Livres sterling)'),
            ('CHF', 'CHF (Francs suisses)'),
        ]
    )

    statut = models.CharField(
        max_length=20,
        choices=STATUT_CHOICES,
        default='EN_ATTENTE'
    )

    date_demande = models.DateTimeField(auto_now_add=True)

    @property
    def ref(self):
        """
        Génère une référence unique en utilisant le format: REF-YYMMDDHHMMSS-<id>
        Cette propriété est accessible après la sauvegarde de l'objet (quand id existe)
        """
        if self.id:
            now = self.date_demande.strftime("%y%m%d%H%M%S")
            return f"REF-{now}"
        return "REF-PENDING"

    def __str__(self):
        return f"{self.nom_client} - {self.commodite} ({self.get_statut_display()})"

    class Meta:
        verbose_name = "Demande de cotation"
        verbose_name_plural = "Demandes de cotation"
        ordering = ['-date_demande']


class EmailQueue(models.Model):
    """
    File d'attente pour les emails à envoyer
    Permet l'envoi différé via cron au lieu de Celery
    """
    
    EMAIL_TYPE_CHOICES = [
        ('CLIENT_CONFIRMATION', 'Confirmation client'),
        ('ADMIN_NOTIFICATION', 'Notification admin'),
    ]
    
    demande = models.ForeignKey(
        DemandeCotation,
        on_delete=models.CASCADE,
        related_name='emails'
    )
    
    email_type = models.CharField(
        max_length=50,
        choices=EMAIL_TYPE_CHOICES
    )
    
    to_email = models.EmailField()
    cc_emails = models.TextField(blank=True, help_text='Emails en copie, séparés par des virgules')
    subject = models.CharField(max_length=255)
    html_content = models.TextField()
    text_content = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    sent = models.BooleanField(default=False)
    sent_at = models.DateTimeField(null=True, blank=True)
    
    attempts = models.IntegerField(default=0)
    error_message = models.TextField(blank=True)
    
    class Meta:
        verbose_name = "Email en attente"
        verbose_name_plural = "Emails en attente"
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['sent', 'created_at']),
            models.Index(fields=['demande']),
        ]
    
    def __str__(self):
        status = "✓ Envoyé" if self.sent else "⏳ En attente"
        return f"{status} - {self.email_type} pour {self.demande.ref}"