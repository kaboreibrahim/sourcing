from django.db import models
from django.contrib.auth.models import AbstractUser
from safedelete.models import SafeDeleteModel, SOFT_DELETE_CASCADE
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
import pyotp
import uuid
from simple_history.models import HistoricalRecords

#### models User  personaliser ########
class Utilisateur(AbstractUser, SafeDeleteModel):
    
    """
    Customized user model inheriting from Django's AbstractUser.
    - `phone`: User's phone number.
    - `gender`: Gender with predefined choices (Male, Female, Other).
    - `country`: Associated country of the user (optional).
    - `city`: Associated city of the user (optional).
    - History tracking and login/logout signals to manage online status.
    """
    GENDER_CHOICES = [
        ('H', _('Homme')),
        ('F', _('Femme')),
        ('A', _('Autre'))
    ]

    TYPES_USER = [
        ('C', _('Client')),
        ('G', _('Gestionnaire')),
        ('A', _('Administrateur'))
    ]

    phone = models.CharField(
        _("Phone Number"), 
        max_length=15, 
        blank=True
    )
    gender = models.CharField(
        _("Gender"), 
        max_length=1, 
        choices=GENDER_CHOICES, 
        blank=True
    )
    
    type_user = models.CharField(
        _("type user"), 
        max_length=1, 
        choices=TYPES_USER, 
        blank=True,
        default='C'  # Default value set to 'C' for Client
    )
    created_at = models.DateTimeField(
        _("Creation Timestamp"), 
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        _("Last Update Timestamp"), 
        auto_now=True
    )
    _safedelete_policy = SOFT_DELETE_CASCADE
    
    
    
    # Ajout de related_name pour éviter les conflits
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='customuser_set',
        related_query_name='customuser',
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='customuser_set',
        related_query_name='customuser',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )
    is_verified = models.BooleanField(default=False)
    
    is_online = models.BooleanField(default=False)  # champ pour le statut en ligne
    
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='personnel_set',  # Ajoutez un related_name unique
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
        verbose_name='groups',
    )
    
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='personnel_permissions_set',  # Ajoutez un related_name unique
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )
    history = HistoricalRecords(table_name='CustomUser_history', history_id_field=models.UUIDField(default=uuid.uuid4))

    
    # Signaux pour mettre à jour le statut en ligne et la date de dernière connexion
    @receiver(user_logged_in)
    def user_logged_in_handler(sender, request, user, **kwargs):
        user.is_online = True
        user.last_login = timezone.now()  # Met à jour le champ last_login
        user.save()

    @receiver(user_logged_out)
    def user_logged_out_handler(sender, request, user, **kwargs):
        user.is_online = False
        user.save()
    

    # Signaux pour mettre à jour le statut en ligne et la date de dernière connexion
    @receiver(user_logged_in)
    def user_logged_in_handler(sender, request, user, **kwargs):
        user.is_online = True
        user.last_login = timezone.now()  # Met à jour le champ last_login
        user.save()

    @receiver(user_logged_out)
    def user_logged_out_handler(sender, request, user, **kwargs):
        user.is_online = False
        user.save()
        
     # New fields for two-factor authentication
    two_factor_method = models.CharField(
        max_length=20, 
        choices=[
            ('email', 'Email Code'),
            ('google_auth', 'Google Authenticator')
        ],
        null=True,
        blank=True
    )
    google_auth_secret = models.CharField(max_length=32, null=True, blank=True)
    
    def generate_google_auth_secret(self):
        if not self.google_auth_secret:
            self.google_auth_secret = pyotp.random_base32()
            self.save()
        return self.google_auth_secret
    
    def verify_google_auth_code(self, code):
        if not self.google_auth_secret:
            return False
        totp = pyotp.TOTP(self.google_auth_secret)
        return totp.verify(code)
    
    def __str__(self):
        return f"{self.username}"