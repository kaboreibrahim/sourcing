from django.db import models

class DemandeCotation(models.Model):

    INCOTERMS_CHOICES = [
        ('EXW', 'EXW'),
        ('FOB', 'FOB'),
        ('CIF', 'CIF'),
        ('CFR', 'CFR'),
    ]

    CONDITIONNEMENT_CHOICES = [
        ('VRAC', 'Vrac'),
        ('FUT', 'Fût'),
        ('BIDON', 'Bidon'),
        ('SAC', 'Sac'),
        ('CONTENEUR', 'Conteneur'),
        ('AUTRE', 'Autre'),
    ]

    STATUT_CHOICES = [
        ('EN_ATTENTE', 'En attente'),
        ('TRAITEE', 'Traitée'),
        ('REFUSEE', 'Refusée'),
    ]

    nom_client = models.CharField(max_length=255)
    contact = models.CharField(max_length=50)

    commodite = models.CharField(max_length=255)
    quantite = models.DecimalField(max_digits=10, decimal_places=2)

    type_conditionnement = models.CharField(
        max_length=20,
        choices=CONDITIONNEMENT_CHOICES,
        default='CONTENEUR'
    )

    incoterm = models.CharField(
        max_length=10,
        choices=INCOTERMS_CHOICES,
        default='FOB'
    )

    pol = models.CharField("Port de chargement (POL)", max_length=255)
    pod = models.CharField("Port de déchargement (POD)", max_length=255)

    target_price = models.DecimalField(max_digits=10, decimal_places=2)

    statut = models.CharField(
        max_length=20,
        choices=STATUT_CHOICES,
        default='EN_ATTENTE'
    )

    date_demande = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nom_client} - {self.commodite} ({self.get_statut_display()})"
