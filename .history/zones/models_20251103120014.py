from django.db import models
from django.utils.translation import gettext_lazy as _
from safedelete.models import SafeDeleteModel, SOFT_DELETE_CASCADE
from simple_history.models import HistoricalRecords
import uuid


class Zone(SafeDeleteModel):
    """
    Modèle représentant une zone géographique.
    - `id`: Identifiant unique de la zone (UUID).
    - `numero`: Numéro de la zone (auto-incrémenté).
    - `description`: Description de la zone.
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
    
    numero = models.IntegerField(
        _("Numéro de zone"),
        unique=True,
        editable=False,  # Non modifiable par l'utilisateur
        help_text="Numéro d'identification de la zone (généré automatiquement)"
    )
    
    description = models.CharField(
        _("Description"),
        max_length=255,
        blank=True,
        null=True
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
        table_name='zone_history',
        history_id_field=models.UUIDField(default=uuid.uuid4)
    )
    
    class Meta:
        verbose_name = _("Zone")
        verbose_name_plural = _("Zones")
        ordering = ['numero']
        db_table = 'zone'
    
    def save(self, *args, **kwargs):
        """
        Surcharge de la méthode save pour auto-générer le numéro de zone
        de manière séquentielle (1, 2, 3, ...)
        """
        if not self.numero:
            # Récupérer le dernier numéro de zone
            derniere_zone = Zone.objects.all().order_by('-numero').first()
            
            if derniere_zone:
                self.numero = derniere_zone.numero + 1
            else:
                self.numero = 1  # Première zone
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Zone {self.numero} - {self.description or 'Sans description'}"
    
    @property
    def nombre_villes(self):
        """Retourne le nombre de villes dans cette zone"""
        return self.villes.count()
    
    @property
    def ville_reference(self):
        """Retourne la ville de référence de cette zone"""
        return self.villes.filter(est_ville_reference=True).first()