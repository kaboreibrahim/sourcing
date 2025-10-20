from django.db import models
from django.contrib.auth.models import AbstractUser
from safedelete.models import SafeDeleteModel, SOFT_DELETE_CASCADE
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
import pyotp
import uuid
from simple_history.models import HistoricalRecords
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver

def upload_to_utilisateur_profile(instance, filename):
    """Génère le chemin d'upload pour les photos de profil des utilisateurs"""
    ext = filename.split('.')[-1]
    filename = f"{instance.id}.{ext}"
    return f"utilisateurs/{instance.username}/profil/{filename}"


#### models User  personaliser ########
class Utilisateur(AbstractUser, SafeDeleteModel):
    
    """
    Model utilisateur personaliser inheriting from Django's AbstractUser.
    - `phone`: User's phone number.
    - `photo_profil`: User's profile photo.
    - `type_user`: User's type with predefined choices (Agent Sourcing, Agent operationnel).
    - `created_at`: Timestamp when the user was created.
    - `updated_at`: Timestamp when the user was last updated.
    - `is_verified`: Boolean field to track if the user's email is verified.
    - `is_online`: Boolean field to track if the user is online.
    - `groups`: Many-to-many relationship with Django's Group model.
    - `user_permissions`: Many-to-many relationship with Django's Permission model.
    """
    

    TYPES_USER = [
        ('AS', _('Agent Sourcing')),
        ('AO', _('Agent operationnel')),
     ]

    phone = models.CharField(
        _("numero de telephone"), 
        max_length=15, 
        blank=True
    )

    photo_profil = models.ImageField(upload_to=upload_to_utilisateur_profile, blank=True)

    
    type_user = models.CharField(
        _("type utilisateur"), 
        max_length=2, 
        choices=TYPES_USER, 
        blank=True,
        default='AS'  # Default value set to 'AS' for Agent Sourcing
    )
    created_at = models.DateTimeField(
        _("creation"), 
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        _("mise a jour"), 
        auto_now=True
    )
    _safedelete_policy = SOFT_DELETE_CASCADE
    
    
    
    # Ajout de related_name pour éviter les conflits
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='utilisateur_set',
        related_query_name='utilisateur',
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='utilisateur_set',
        related_query_name='utilisateur',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )
    is_verified = models.BooleanField(default=False)
    
    is_online = models.BooleanField(default=False)  # champ pour le statut en ligne
    
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='utilisateur_set',  # Ajoutez un related_name unique
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
        verbose_name='groups',
    )
    
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='utilisateur_permissions_set',  # Ajoutez un related_name unique
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )
    history = HistoricalRecords(table_name='Utilisateur_history', history_id_field=models.UUIDField(default=uuid.uuid4))

    
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



class VerificationCode(models.Model):
    user = models.OneToOneField(Utilisateur, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.code}"