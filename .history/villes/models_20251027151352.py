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
    
    distance_port_abidjan = models.DecimalField(
        _("Distance du port d'Abidjan"),
        max_digits=15,
        decimal_places=2,
        blank=True,
        null=True,
        help_text="Distance entre la ville et le port d'Abidjan"
    )
    
    distance_port_sanpedro = models.DecimalField(
        _("Distance du port de San-Pedro"),
        max_digits=15,
        decimal_places=2,
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
    
    est_ville_reference = models.BooleanField(
        _("Ville de référence"),
        default=False,
        help_text="Cochez pour définir cette ville comme ville de référence pour sa zone"
    )
    
    zone = models.ForeignKey(
        'zones.Zone',  # Référence à l'app zones
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
        indexes = [
            models.Index(fields=['est_ville_reference', 'zone']),
        ]
    
    def __str__(self):
        reference = " ⭐" if self.est_ville_reference else ""
        return f"{self.nom} - Zone {self.zone.numero}{reference}"
    
    def save(self, *args, **kwargs):
        """
        Surcharge de la méthode save pour garantir qu'il n'y a qu'une seule 
        ville de référence par zone
        """
        if self.est_ville_reference:
            # Retirer le statut de ville de référence aux autres villes de la même zone
            Ville.objects.filter(
                zone=self.zone, 
                est_ville_reference=True
            ).exclude(id=self.id).update(est_ville_reference=False)
        
        super().save(*args, **kwargs)
    
    @classmethod
    def get_ville_reference_par_zone(cls, zone):
        """Retourne la ville de référence d'une zone donnée"""
        try:
            return cls.objects.get(zone=zone, est_ville_reference=True)
        except cls.DoesNotExist:
            return None
        except cls.MultipleObjectsReturned:
            # Si plusieurs villes sont marquées comme référence, retourner la première
            return cls.objects.filter(zone=zone, est_ville_reference=True).first()



class Localite(SafeDeleteModel):
    """
    Modèle représentant une localité.
    - `id`: Identifiant unique de la localité (UUID).
    - `nom`: Nom de la localité.
    - `distance_port_abidjan`: Distance entre la localité et le port d'Abidjan.
    - `distance_port_sanpedro`: Distance entre la localité et le port de San-Pedro.
    - `ville`: Ville à laquelle appartient la localité.
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
        "Nom de la localité",
        max_length=100,
        unique=True
    )

    distance_port_abidjan = models.DecimalField(
        _("Distance du port d'Abidjan"),
        max_digits=15,
        decimal_places=2,
        blank=True,
        null=True,
        help_text="Distance entre la ville et le port d'Abidjan"
    )
    
    distance_port_sanpedro = models.DecimalField(
        _("Distance du port de San-Pedro"),
        max_digits=15,
        decimal_places=2,
        blank=True,
        null=True,
        help_text="Distance entre la ville et le port de San-Pedro"
    )
    
    ville = models.ForeignKey(Ville, on_delete=models.CASCADE)
    
    created_at = models.DateTimeField(
        "Date de création",
        auto_now_add=True
    )
    
    updated_at = models.DateTimeField(
        "Date de mise à jour",
        auto_now=True
    )
    
    history = HistoricalRecords(
        table_name='localite_history',
        history_id_field=models.UUIDField(default=uuid.uuid4)
    )
    
    class Meta:
        verbose_name = "Localité"
        verbose_name_plural = "Localités"
        ordering = ['nom']
        db_table = 'localite'
        indexes = [
            models.Index(fields=['ville']),
        ]
    
    def __str__(self):
        return f"{self.nom} ({self.ville.nom})"
    
    def save(self, *args, **kwargs):
        """
        Surcharge de la méthode save pour garantir qu'il n'y a qu'une seule 
        localité par ville
        """
        if self.ville:
            # Retirer la localité de la ville si elle existe déjà
            Localite.objects.filter(ville=self.ville).exclude(id=self.id).update(ville=None)
        
        super().save(*args, **kwargs)
