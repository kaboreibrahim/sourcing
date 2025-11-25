from django.db import models
from django.utils.translation import gettext_lazy as _
from safedelete.models import SafeDeleteModel, SOFT_DELETE_CASCADE
from simple_history.models import HistoricalRecords
import uuid
from Pays.models import Pays
from fournisseurs.models import Fournisseur

class Port(SafeDeleteModel):
    """
    Modèle représentant un port.
    - `id`: Identifiant unique du port (UUID).
    - `nom`: Nom du port.
    -`latitude`: Latitude du port.
    - `longitude`: Longitude du port.
    - `pays`: Pays auquel appartient le port.
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

    nom=models.CharField(
        "Nom du port",
        max_length=150,
        unique=True
    )

    latitude = models.FloatField(
        null=True, 
        blank=True, 
        verbose_name="Latitude "
    )
    
    longitude= models.FloatField(
        null=True, 
        blank=True, 
        verbose_name="Longitude "
    )

    pays=models.ForeignKey(
        Pays,
        on_delete=models.CASCADE,
        verbose_name="Pays"
    )

    created_at = models.DateTimeField(
        "Date de création",
        auto_now_add=True
    )
    
    updated_at = models.DateTimeField(
        "Date de mise à jour",
        auto_now=True
    )
    
    history = HistoricalRecords(
        table_name='port_history',
        history_id_field=models.UUIDField(default=uuid.uuid4)
    )
    
    class Meta:
        verbose_name = "Port"
        verbose_name_plural = "Ports"
        ordering = ['nom']
        db_table = 'port'
    
    def __str__(self):
        return self.nom


class FournisseurPort(SafeDeleteModel):
    """
    Modèle de liaison entre un Fournisseur et un Port.
    Permet de gérer plusieurs fournisseurs pour une même commodité.
    """
    _safedelete_policy = SOFT_DELETE_CASCADE

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    fournisseur = models.ForeignKey(
        'fournisseurs.Fournisseur',
        on_delete=models.CASCADE,
        related_name='liens_commodites',
        verbose_name=_("Fournisseur")
    )

    port = models.ForeignKey(
        'port.Port',
        on_delete=models.CASCADE,
        related_name='liens_fournisseurs',
        verbose_name=_("Port")
    )

   
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'fournisseur_port'
        verbose_name = _("Lien Fournisseur-Port")
        verbose_name_plural = _("Liens Fournisseur-Ports")
        unique_together = [['fournisseur', 'port']]
        indexes = [
            models.Index(fields=['fournisseur']),
            models.Index(fields=['commodite']),
        ]

    def __str__(self):
        return f"{self.fournisseur.nom} - {self.commodite.nom}"



