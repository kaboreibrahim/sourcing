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


    contact = models.CharField(
        _("Contact"),
        max_length=17,
        validators=[phone_regex],
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
    
    localite = models.ForeignKey(
        'villes.Localite',  # Référence à l'app villes
        on_delete=models.PROTECT,
        related_name='fournisseurs',
        verbose_name=_("Localité"),
        blank=True,
        null=True,
        help_text="Localité précise du fournisseur"
    )
    
    ville = models.ForeignKey(
        'villes.Ville',  # Référence à l'app villes
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

    def calculate_distance(self):
        """
        Calcule la distance en kilomètres entre le port et le fournisseur en utilisant l'API Mapbox
        et met à jour le champ distance.
        Retourne la distance calculée ou None en cas d'erreur.
        """
        import requests
        from django.conf import settings
        
        # Vérifier que les coordonnées existent
        if not all([self.port.latitude, self.port.longitude, 
                   self.ville.latitude, self.ville.longitude]):
            return None
            
        # Récupérer le token Mapbox depuis les paramètres
        mapbox_token = getattr(settings, 'MAPBOX_ACCESS_TOKEN', '')
        if not mapbox_token:
            return None
            
        # Coordonnées au format lon,lat pour Mapbox
        origin = f"{self.port.longitude},{self.port.latitude}"
        destination = f"{self.ville.longitude},{self.ville.latitude}"
        
        # URL de l'API Mapbox Matrix
        url = (
            f"https://api.mapbox.com/directions-matrix/v1/mapbox/driving/"
            f"{origin};{destination}?access_token={mapbox_token}&annotations=distance"
        )
        
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                # La distance est en mètres, on convertit en kilomètres
                distance_km = data['distances'][0][1] / 1000
                self.distance = round(distance_km, 2)
                self.save(update_fields=['distance'])
                return self.distance
        except (requests.RequestException, KeyError, IndexError) as e:
            # En cas d'erreur, on ne fait rien et on retourne None
            pass
            
        return None
    
    def save(self, *args, **kwargs):
        # Si c'est une nouvelle entrée ou si les coordonnées ont changé
        if not self.pk or ('update_fields' not in kwargs or 'distance' not in kwargs.get('update_fields', [])):
            self.calculate_distance()
        super().save(*args, **kwargs)



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
        related_name='liens_fournisseurs',
        verbose_name=_("Fournisseur")
    )

    port = models.ForeignKey(
        'port.Port',
        on_delete=models.CASCADE,
        related_name='liens_ports',
        verbose_name=_("Port")
    )

    distance=models.DecimalField(
        "Distance",
        max_digits=15,
        decimal_places=2,
        blank=True,
        null=True,
        help_text="Distance entre le port et le fournisseur"
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
            models.Index(fields=['port']),
        ]

    def __str__(self):
        return f"{self.fournisseur.nom} - {self.port.nom}"



