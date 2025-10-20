from django.db import models
from django.utils.translation import gettext_lazy as _
from safedelete.models import SafeDeleteModel, SOFT_DELETE_CASCADE
from simple_history.models import HistoricalRecords
import uuid



class Ville(SafeDeleteModel):
    """
    Modèle représentant une ville.
    - `id`: Identifiant unique de la ville (UUID).
    - `nom`: Nom de la ville.
    - `superficie`: Superficie de la ville en km².
    - `distance_port_abidjan`: Distance par rapport au port d'Abidjan.
    - `distance_port_sanpedro`: Distance par rapport au port de San-Pedro.
    - `description`: Description de la ville.
    - `ville_reference`: Ville de référence.
    - `zone`: Relation avec la zone géographique.
    - `created_at`: Date de création.
    - `updated_at`: Date de mise à jour.
    """
    
    _safedelete_policy = SOFT_DELETE_CASCADE
    
    id = models.UUIDField(
        "Identifiant unique",
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    
    nom = models.CharField(
        _("Nom de la ville"),
        max_length=100,
        unique=True
    )
    
    superficie = models.DecimalField(
        _("Superficie (km²)"),
        max_digits=15,
        decimal_places=2,
        blank=True,
        null=True,
        help_text="Superficie de la ville en kilomètres carrés"
    )
    
    distance_port_abidjan = models.TextField(
        _("Distance du port d'Abidjan"),
        blank=True,
        null=True,
        help_text="Distance entre la ville et le port d'Abidjan"
    )
    
    distance_port_sanpedro = models.TextField(
        _("Distance du port de San-Pedro"),
        blank=True,
        null=True,
        help_text="Distance entre la ville et le port de San-Pedro"
    )
    
    description = models.CharField(
        _("Description"),
        max_length=255,
        blank=True,
        null=True
    )
    
    ville_reference = models.CharField(
        _("Ville de référence"),
        max_length=100,
        blank=True,
        null=True,
        help_text="Ville servant de point de référence"
    )
    
    zone = models.ForeignKey(
        'zone.Zone',  # Référence à l'app zone
        on_delete=models.PROTECT,
        related_name='villes',
        verbose_name=_("Zone"),
        help_text="Zone géographique à laquelle appartient la ville"
    )
    
    created_at = models.DateTimeField(
        _("Date de création"),
        auto_now_add=True
    )
    
    updated_at = models.DateTimeField(
        _("Date de mise à jour"),
        auto_now=True
    )
    
    history = HistoricalRecords(
        table_name='ville_history',
        history_id_field=models.UUIDField(default=uuid.uuid4)
    )
    
    class Meta:
        verbose_name = _("Ville")
        verbose_name_plural = _("Villes")
        ordering = ['nom']
        db_table = 'ville'
    
    def __str__(self):
        return f"{self.nom} - Zone {self.zone.numero}"