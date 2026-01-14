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
import random
import string
from django_lifecycle import LifecycleModel, hook

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
        ('FS', _('Fournisseur')),
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





class CodeVerification(SafeDeleteModel, LifecycleModel):
    """Modèle pour les codes de vérification d'email"""
    _safedelete_policy = SOFT_DELETE_CASCADE
    
    TYPE_CHOICES = [
        ('activation', 'Activation de compte'),
        ('otp', 'Code de vérification'),
        ('password_reset', 'Réinitialisation mot de passe'),
        ('email_change', 'Changement d\'email'),
    ]
    
    id = models.UUIDField(
        "Unique Identifier", 
        primary_key=True, 
        default=uuid.uuid4, 
        editable=False
    )
    user = models.ForeignKey(Utilisateur, on_delete=models.CASCADE, related_name='codes_verification')
    code = models.CharField(max_length=6)
    type_code = models.CharField(max_length=20, choices=TYPE_CHOICES)
    email = models.EmailField()
    is_used = models.BooleanField(default=False)
    attempts = models.PositiveIntegerField(default=0)
    max_attempts = models.PositiveIntegerField(default=3)
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    used_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = "Code de vérification"
        verbose_name_plural = "Codes de vérification"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.code} ({self.type_code})"
    
    @classmethod
    def generate_code(cls):
        """Génère un code à 6 caractères, composé de lettres et de chiffres"""
        return ''.join(random.choices(string.ascii_letters + string.digits, k=6))
    @classmethod
    def create_verification_code(cls, user, type_code, email=None, validity_seconds=180):
        """Crée un nouveau code de vérification"""
        # Invalider les anciens codes non utilisés du même type
        cls.objects.filter(
            user=user,
            type_code=type_code,
            is_used=False
        ).update(is_used=True)
        
        # Créer le nouveau code
        code = cls.generate_code()
        expires_at = timezone.now() + timedelta(seconds=validity_seconds)
        
        return cls.objects.create(
            user=user,
            code=code,
            type_code=type_code,
            email=email or user.email,
            expires_at=expires_at
        )
    
    def is_expired(self):
        """Vérifie si le code a expiré"""
        return self.expires_at is not None and timezone.now() > self.expires_at
    
    def is_valid(self):
        """Vérifie si le code est encore valide"""
        return (
            not self.is_used and 
            not self.is_expired() and 
            self.attempts < self.max_attempts
        )

    
    def mark_as_used(self):
        """Marque le code comme utilisé"""
        self.is_used = True
        self.used_at = timezone.now()
        self.save()
    
    def increment_attempts(self):
        """Incrémente le nombre de tentatives"""
        self.attempts += 1
        self.save()
        return self.attempts >= self.max_attempts
