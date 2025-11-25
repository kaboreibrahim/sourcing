from django.db import models
from django.utils.translation import gettext_lazy as _
from safedelete.models import SafeDeleteModel, SOFT_DELETE_CASCADE
from simple_history.models import HistoricalRecords
import uuid


class Pays(SafeDeleteModel):
    """
    Modele représentant un pays.
    - `id`: Identifiant unique du pays (UUID).
    - `nom`: Nom du pays.
    - `code`: Code ISO du pays.
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
        "Nom du pays",
        max_length=255,
        unique=True,
        help_text="Nom du pays"
    )

    code = models.CharField(
        "Code ISO du pays",
        max_length=2,
        unique=True,
        help_text="Code ISO du pays"
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
        table_name='pays_history',
        history_id_field=models.UUIDField(default=uuid.uuid4)
    )

    class Meta:
        verbose_name = "Pays"
        verbose_name_plural = "Pays"
        ordering = ['nom']
        db_table = 'pays'

