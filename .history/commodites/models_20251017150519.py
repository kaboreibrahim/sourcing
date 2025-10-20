from django.db import models
from django.utils.translation import gettext_lazy as _
from safedelete.models import SafeDeleteModel, SOFT_DELETE_CASCADE
from simple_history.models import HistoricalRecords
import uuid


class Commodite(SafeDeleteModel):
    """
    Modèle représentant une commodité (produit agricole).
    - `id`: Identifiant unique de la commodité (UUID).
    - `nom`: Nom de la commodité.
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
        _("Nom de la commodité"),
        max_length=150,
        help_text="Type de produit agricole (ex: Cacao, Café, Noix de cajou, etc.)"
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
        table_name='commodite_history',
        history_id_field=models.UUIDField(default=uuid.uuid4)
    )
    
    class Meta:
        verbose_name = _("Commodité")
        verbose_name_plural = _("Commodités")
        ordering = ['nom']
        db_table = 'commodite'
        unique_together = [['nom']]
        indexes = [
            models.Index(fields=['nom']),
        ]
    
    def __str__(self):
        return f"{self.nom}"
    
