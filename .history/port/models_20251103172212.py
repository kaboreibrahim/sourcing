from django.db import models
from django.utils.translation import gettext_lazy as _
from safedelete.models import SafeDeleteModel, SOFT_DELETE_CASCADE
from simple_history.models import HistoricalRecords
import uuid
from Pays.models import Pays


class Port(SafeDeleteModel):
    """
    Modèle représentant un port.
    - `id`: Identifiant unique du port (UUID).
    - `nom`: Nom du port.
    -`latidr`: Pays auquel appartient le port.
    - `code`: Code  du port.
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