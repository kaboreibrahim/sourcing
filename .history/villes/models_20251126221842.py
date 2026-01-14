from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from safedelete.models import SafeDeleteModel, SOFT_DELETE_CASCADE
from simple_history.models import HistoricalRecords
import uuid


######## ville ########
class Ville(SafeDeleteModel):
    """
    Modèle représentant une ville.
    - `id`: Identifiant unique de la ville (UUID).
    - `nom`: Nom de la ville.
    - `superficie`: Superficie de la ville en km².
    - `latitude`: Latitude de la ville.
    - `longitude`: Longitude de la ville.
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


######## ville & port ########

class VillePort(SafeDeleteModel):

    _safedelete_policy = SOFT_DELETE_CASCADE
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    
    port = models.ForeignKey(
        'port.Port',
        on_delete=models.CASCADE,
        related_name='ville_ports',  # <- unique !
        verbose_name=_("Port")
    )

    ville = models.ForeignKey(
        'villes.Ville',
        on_delete=models.CASCADE,
        related_name='ports_villes',  # <- unique aussi
        verbose_name=_("Ville")
    )

    distance = models.DecimalField(
        "Distance",
        max_digits=15,
        decimal_places=2,
        blank=True,
        null=True,
        help_text="Distance entre le port et la ville"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'ville_port'
        verbose_name = _("Lien Ville-Port")
        verbose_name_plural = _("Liens Ville-Ports")
        unique_together = [['ville', 'port']]
        indexes = [
            models.Index(fields=['ville']),
            models.Index(fields=['port']),
        ]

    def calculate_distance(self):
        """
        Calcule la distance en kilomètres entre le port et la ville en utilisant l'API Mapbox
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
    
    def __str__(self):
        return f"{self.port.nom} - {self.ville.nom}"


######## localite ########
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
    
    superficie = models.DecimalField(
        _("Superficie (km²)"),
        max_digits=15,
        decimal_places=2,
        blank=True,
        null=True,
        help_text="Superficie de la localité en kilomètres carrés"
    )
    ville = models.ForeignKey(
        Ville,
        on_delete=models.CASCADE,
        related_name="localites"
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
        table_name='localite_history',
        history_id_field=models.UUIDField(default=uuid.uuid4)
    )
    
    class Meta:
        verbose_name = "Localité"
        verbose_name_plural = "Localités"
        ordering = ['nom']²
        db_table = 'localite'
        indexes = [
            models.Index(fields=['ville']),
        ]
    
    def __str__(self):
        return f"{self.nom} ({self.ville.nom})"
    
    def save(self, *args, **kwargs):
        """
        Surcharge de la méthode save pour sauvegarder la localité
        """
        # Vérification de l'unicité du nom de la localité
        if Localite.objects.filter(nom=self.nom).exclude(id=getattr(self, 'id', None)).exists():
            raise ValidationError("Une localité avec ce nom existe déjà.")
        
        # Appel de la méthode save de la classe parente
        super().save(*args, **kwargs)

class PortLocalite(SafeDeleteModel):
    _safedelete_policy = SOFT_DELETE_CASCADE
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    
    port = models.ForeignKey(
        'port.Port',
        on_delete=models.CASCADE,
        related_name='localite_ports',  # <- unique
        verbose_name=_("Port")
    )

    localite = models.ForeignKey(
        'villes.Localite',
        on_delete=models.CASCADE,
        related_name='ports_localites',  # <- unique
        verbose_name=_("Localité")
    )

    distance = models.DecimalField(
        "Distance",
        max_digits=15,
        decimal_places=2,
        blank=True,
        null=True,
        help_text="Distance entre le port et la localité"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'port_localite'
        verbose_name = _("Lien Port-Localite")
        verbose_name_plural = _("Liens Port-Localites")
        unique_together = [['port', 'localite']]
        indexes = [
            models.Index(fields=['port']),
            models.Index(fields=['localite']),
        ]


    
    def calculate_distance(self):
        """
        Calcule la distance en kilomètres entre le port et la localité en utilisant l'API Mapbox
        et met à jour le champ distance.
        Retourne la distance calculée ou None en cas d'erreur.
        """
        import requests
        from django.conf import settings
        
        # Vérifier que les coordonnées existent
        if not all([self.port.latitude, self.port.longitude, 
                   self.localite.latitude, self.localite.longitude]):
            return None
            
        # Récupérer le token Mapbox depuis les paramètres
        mapbox_token = getattr(settings, 'MAPBOX_ACCESS_TOKEN', '')
        if not mapbox_token:
            return None
            
        # Coordonnées au format lon,lat pour Mapbox
        origin = f"{self.port.longitude},{self.port.latitude}"
        destination = f"{self.localite.longitude},{self.localite.latitude}"
        
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
    
    def __str__(self):
        return f"{self.port.nom} - {self.localite.nom}"
