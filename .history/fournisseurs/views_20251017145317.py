from django.db import models
from django.utils.translation import gettext_lazy as _
from safedelete.models import SafeDeleteModel, SOFT_DELETE_CASCADE
from simple_history.models import HistoricalRecords
from django.core.validators import RegexValidator
import uuid


def upload_to_fournisseur_documents(instance, filename):
    """Génère le chemin d'upload pour les documents des fournisseurs"""
    ext = filename.split('.')[-1]
    return f"fournisseurs/{instance.id}/documents/{filename}"


class Fournisseur(SafeDeleteModel):
    """
    Modèle représentant un fournisseur.
    - `id`: Identifiant unique du fournisseur (UUID).
    - `nom`: Nom du fournisseur.
    - `nom_responsable`: Nom du responsable du fournisseur.
    - `longitude`: Coordonnée géographique (longitude).
    - `latitude`: Coordonnée géographique (latitude).
    - `contact`: Numéro de contact du fournisseur.
    - `distance_port_abidjan`: Distance par rapport au port d'Abidjan.
    - `distance_port_sanpedro`: Distance par rapport au port de San-Pedro.
    - `document_fourni_aex`: Documents fournis (AEX).
    - `localite`: Localité du fournisseur.
    - `ville`: Relation avec la ville.
    - `created_at`: Date de création.
    - `updated_at`: Date de mise à jour.
    """
    
    _safedelete_policy = SOFT_DELETE_CASCADE
    
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Le numéro de téléphone doit être au format: '+999999999'. Jusqu'à 15 chiffres autorisés."
    )
    
    id = models.UUIDField(
        "Identifiant unique",
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    
    nom = models.CharField(
        _("Nom du fournisseur"),
        max_length=150,
        unique=True
    )
    
    nom_responsable = models.CharField(
        _("Nom du responsable"),
        max_length=150,
        blank=True,
        null=True
    )
    
    latitude = models.DecimalField(
        max_digits=6, 
        decimal_places=5, 
        null=True, 
        blank=True, 
        verbose_name="Latitude de destination"
    )
    
    longitude= models.DecimalField(
        max_digits=6, 
        decimal_places=5, 
        null=True, 
        blank=True, 
        verbose_name="Longitude de destination"
    )
    Contact_destinateur = models.CharField(max_length=255, blank=True, null=True)

    contact = models.CharField(
        _("Contact"),
        validators=[phone_regex],
        max_length=17,
        blank=True,
        null=True
    )
    
    distance_port_abidjan = models.CharField(
        _("Distance du port d'Abidjan"),
        max_length=100,
        blank=True,
        null=True
    )
    
    distance_port_sanpedro = models.CharField(
        _("Distance du port de San-Pedro"),
        max_length=100,
        blank=True,
        null=True
    )
    
    document_fourni_aex = models.FileField(
        _("Document fourni (AEX)"),
        upload_to=upload_to_fournisseur_documents,
        blank=True,
        null=True,
        help_text="Documents administratifs du fournisseur"
    )
    
    localite = models.CharField(
        _("Localité"),
        max_length=150,
        blank=True,
        null=True,
        help_text="Localité précise du fournisseur"
    )
    
    ville = models.ForeignKey(
        'ville.Ville',  # Référence à l'app ville
        on_delete=models.PROTECT,
        related_name='fournisseurs',
        verbose_name=_("Ville"),
        help_text="Ville où se trouve le fournisseur"
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
        table_name='fournisseur_history',
        history_id_field=models.UUIDField(default=uuid.uuid4)
    )
    
    class Meta:
        verbose_name = _("Fournisseur")
        verbose_name_plural = _("Fournisseurs")
        ordering = ['nom']
        db_table = 'fournisseur'
        indexes = [
            models.Index(fields=['nom']),
            models.Index(fields=['ville']),
        ]
    
    def __str__(self):
        return f"{self.nom} - {self.ville.nom}"
    
    @property
    def get_zone(self):
        """Retourne la zone du fournisseur via la ville"""
        return self.ville.zone if self.ville else None