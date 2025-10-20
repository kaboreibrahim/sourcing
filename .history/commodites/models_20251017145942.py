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
    - `fournisseur`: Relation avec le fournisseur.
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
    
    fournisseur = models.ForeignKey(
        'fournisseur.Fournisseur',  # Référence à l'app fournisseur
        on_delete=models.CASCADE,
        related_name='commodites',
        verbose_name=_("Fournisseur"),
        help_text="Fournisseur de cette commodité"
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
        ordering = ['nom', 'fournisseur']
        db_table = 'commodite'
        unique_together = [['nom', 'fournisseur']]
        indexes = [
            models.Index(fields=['nom']),
            models.Index(fields=['fournisseur']),
        ]
    
    def __str__(self):
        return f"{self.nom} - {self.fournisseur.nom}"
    
    @property
    def get_ville(self):
        """Retourne la ville du fournisseur"""
        return self.fournisseur.ville if self.fournisseur else None
    
    @property
    def get_zone(self):
        """Retourne la zone du fournisseur"""
        return self.fournisseur.ville.zone if self.fournisseur and self.fournisseur.ville else None