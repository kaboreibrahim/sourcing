from django.db import models
from django.utils.translation import gettext_lazy as _
from safedelete.models import SafeDeleteModel, SOFT_DELETE_CASCADE
from simple_history.models import HistoricalRecords
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
import uuid



class Echantionnage(SafeDeleteModel):
    """
    Modèle représentant un échantillonnage de commodité.
    - `id`: Identifiant unique de l'échantillonnage (UUID).
    - `reference`: Référence de l'échantillon.
    - `quantite`: Quantité échantillonnée.
    - `date_creation`: Date de création de l'échantillon.
    - `taux_acidite_ffa`: Taux d'acidité (FFA - Free Fatty Acid).
    - `impurete_insolubles`: Taux d'impuretés insolubles.
    - `teneur_eau_matiere_volatiles_mnl`: Teneur en eau et matières volatiles (MNL).
    - `utilisateur`: Agent ayant effectué l'échantillonnage.
    - `commodite`: Commodité échantillonnée.
    - `created_at`: Date d'enregistrement dans le système.
    - `updated_at`: Date de mise à jour.
    """
    
    _safedelete_policy = SOFT_DELETE_CASCADE
    
    id = models.UUIDField(
        "Identifiant unique",
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    
    def save(self, *args, **kwargs):
        if not self.reference:
            self.reference = f"ECH-{self.id}"
        super().save(*args, **kwargs)

    reference = models.CharField(
        _("Référence"),
        max_length=50,
        unique=True,
        editable=False,
        help_text="Référence unique de l'échantillon"
    )
    
    quantite = models.DecimalField(
        _("Quantité"),
        max_digits=12,
        decimal_places=2,
        help_text="Quantité (tonne)"
    )
    
    prix = models.DecimalField(
        _("Prix en FCFA/Tonne"),
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Prix d'achat ou de vente selon la relation"
    )
    date_creation = models.DateTimeField(
        _("Date de création"),
        default=timezone.now,
        help_text="Date à laquelle l'enregistrement a été créé"
    )
    
    taux_acidite_ffa = models.DecimalField(
        _("Taux d'acidité (FFA %)"),
        max_digits=5,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(100)
        ],
        help_text="Taux d'acides gras libres (Free Fatty Acid) en pourcentage"
    )
    
    impurete_insolubles = models.DecimalField(
        _("Impuretés insolubles (%)"),
        max_digits=5,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(100)
        ],
        help_text="Pourcentage d'impuretés insolubles"
    )
    
     
    teneur_eau_matiere_volatiles_mnl = models.DecimalField(
        _("Teneur en eau et matières volatiles (MNL %)"),
        max_digits=5,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(100)
        ],
        help_text="Teneur en eau et matières volatiles (Moisture and Not Lipid) en pourcentage"
    )
    
    utilisateur = models.ForeignKey(
        'utilisateur.Utilisateur',  # Référence à l'app utilisateur
        on_delete=models.PROTECT,
        related_name='echantillonnages',
        verbose_name=_("Agent"),
        help_text="Agent ayant effectué l'échantillonnage"
    )
    
    commodite = models.ForeignKey(
        'commodites.Commodite',  # Référence à l'app commodites
        on_delete=models.PROTECT,
        related_name='echantillonnages',
        verbose_name=_("Commodité"),
        help_text="Commodité échantillonnée"
    )
    
    fournisseur = models.ForeignKey(
        'fournisseurs.Fournisseur',
        on_delete=models.PROTECT,
        related_name='echantillonnages',
        verbose_name=_("Fournisseur"),
        help_text="Fournisseur source de la marchandise"
    )
    
    quantite_totale = models.DecimalField(
        _("Quantité totale (tonnes)"),
        max_digits=15,
        decimal_places=2,
        default=0,
        help_text="Quantité totale pour cette commodité et ce fournisseur"
    )
    
    created_at = models.DateTimeField(
        _("Date d'enregistrement"),
        auto_now_add=True
    )
    
    updated_at = models.DateTimeField(
        _("Date de mise à jour"),
        auto_now=True
    )
    
    history = HistoricalRecords(
        table_name='echantionnage_history',
        history_id_field=models.UUIDField(default=uuid.uuid4)
    )
    
    class Meta:
        verbose_name = _("Échantillonnage")
        verbose_name_plural = _("Échantillonnages")
        ordering = ['-date_creation']
        db_table = 'echantionnage'
        indexes = [
            models.Index(fields=['reference']),
            models.Index(fields=['date_creation']),
            models.Index(fields=['utilisateur']),
            models.Index(fields=['commodite']),
        ]
    
    def __str__(self):
        return f"{self.reference} - {self.commodite.nom} ({self.date_creation.strftime('%d/%m/%Y')})"
    
    # @property
    # def fournisseur(self):
    #     """Retourne le fournisseur de la commodité"""
    #     return self.commodite.fournisseur if self.commodite else None
    
    # @property
    # def ville(self):
    #     """Retourne la ville du fournisseur"""
    #     return self.commodite.get_ville if self.commodite else None
    
    # @property
    # def zone(self):
    #     """Retourne la zone du fournisseur"""
    #     return self.commodite.get_zone if self.commodite else None
    
    @property
    def est_conforme(self):
        """
        Vérifie si l'échantillon est conforme aux normes.
        À adapter selon vos critères de conformité.
        """
        if not all([self.taux_acidite_ffa, self.impurete_insolubles, self.teneur_eau_matiere_volatiles_mnl]):
            return None  # Données incomplètes
        
        # Exemple de critères (à adapter selon vos normes)
        return (
            self.taux_acidite_ffa <= 3.0 and
            self.impurete_insolubles <= 0.5 and
            self.teneur_eau_matiere_volatiles_mnl <= 0.2
        )

    # def pourcentage (self) :
