from django.db import models

class DemandeCotation(models.Model):

    INCOTERMS_CHOICES = [
        ('EXW', 'EXW'),
        ('FOB', 'FOB'),
        ('CIF', 'CIF'),
        ('CFR', 'CFR'),
        ('DAP', 'DAP'),
        ('DDP', 'DDP'),
    ]

    CONDITIONNEMENT_CHOICES = [
        ('VRAC', 'Vrac'),
        ('FUT', 'Fût'),
        ('BIDON', 'Bidon'),
        ('SAC', 'Sac'),
        ('CONTENEUR', 'Conteneur'),
        ('AUTRE', 'Autre'),
    ]

    nom_client = models.CharField(max_length=255)
    contact = models.CharField(max_length=50)

    commodite = models.CharField(max_length=255)
    quantite = models.DecimalField(max_digits=10, decimal_places=2)

    type_conditionnement = models.CharField(
        max_length=20,
        choices=CONDITIONNEMENT_CHOICES
    )

    incoterm = models.CharField(
        max_length=10,
        choices=INCOTERMS_CHOICES
    )

    pol = models.CharField("Port de chargement (POL)", max_length=255)
    pod = models.CharField("Port de déchargement (POD)", max_length=255)

    target_price = models.DecimalField(max_digits=10, decimal_places=2)

    date_demande = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nom_client} - {self.commodite}"
