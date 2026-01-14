from django.shortcuts import render, redirect
from django.contrib.auth import login,logout,get_backends
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
# view de creation de compte 
from django.contrib.auth.models import User
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import views as auth_views
from utilisateur.forms import LoginForm,TwoFactorMethodForm,GoogleAuthVerificationForm,EmailVerificationForm
from uuid import UUID
import random
from django.core.mail import send_mail
import pyotp
import qrcode
import io
import base64
from utilisateur.models import Utilisateur
from django.templatetags.static import static
from django.contrib.staticfiles.storage import staticfiles_storage
 
class EmailOrUsernameModelBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            # On utilise CustomUser au lieu de User
            user = Utilisateur.objects.get(
                Q(username=username) | Q(email=username)
            )
            # Vérifie si le mot de passe est correct et si l'utilisateur peut s'authentifier
            if user.check_password(password) and self.user_can_authenticate(user):
                return user
            return None
        except Utilisateur.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return Utilisateur.objects.get(pk=user_id)
        except Utilisateur.DoesNotExist:
            return None     

def connexion(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            
            user = form.get_user()
            # Ajouter un print de débug
            print("User ID being stored:", str(user.id))
            request.session['pre_2fa_user_id'] = str(user.id)
            # Vérifier que la session est sauvegardée
            print("Session after storage:", request.session.get('pre_2fa_user_id'))

            return redirect('two_factor_method')
    else:
        form = LoginForm()
    return render(request, 'connexion/login/login.html', {'form': form})

############## Déconnexion ##############
def user_logout(request):
    """Vue de déconnexion"""
    user_name = request.user.get_full_name() or request.user.username
    logout(request)
    messages.success(request, f'Au revoir {user_name} ! Vous êtes déconnecté.')
    return redirect('website:accueil')

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags

def two_factor_method(request):
    print("Session at start:", request.session.get('pre_2fa_user_id'))
    if 'pre_2fa_user_id' not in request.session:
        print("No pre_2fa_user_id in session")
        return redirect('login')
    
    try:
        user_id = request.session['pre_2fa_user_id']
        user = Utilisateur.objects.get(id=user_id)
        print("User found:", user.username)
    except (ValueError, Utilisateur.DoesNotExist) as e:
        print("Error:", str(e))
        del request.session['pre_2fa_user_id']
        return redirect('login')
   
    if request.method == 'POST':
        form = TwoFactorMethodForm(request.POST)
        if form.is_valid():
            method = form.cleaned_data['two_factor_method']
            user.two_factor_method = method
            user.save()
            # Construire l'URL complète du logo
            logo_url = f"{request.scheme}://{request.get_host()}/static/images/logo.png"
           
            if method == 'email':
                code = str(random.randint(100000, 999999))
                request.session['2fa_email_code'] = code
                
                # Préparer le contexte pour le template
                context = {
                    'code': code,
                    'user': user,
                    'logo_url': logo_url
                }
                
                # Charger le template HTML
                html_content = render_to_string('emails/2fa_verification.html', context)
                text_content = strip_tags(html_content)  # Version texte brut
                
                # Créer l'email avec HTML
                email = EmailMultiAlternatives(
                    subject='Code de Vérification - Authentification à Deux Facteurs',
                    body=text_content,
                    from_email='no-reply@sourcing.com',
                    to=[user.email],
                )
                email.attach_alternative(html_content, "text/html")
                email.send(fail_silently=False)
                
                return redirect('email_verification')
           
            elif method == 'google_auth':
                # Check if user already has Google Auth set up
                if user.google_auth_secret:
                    return redirect('google_auth_verification')
                    
                # If not set up, continue with new setup
                secret = user.generate_google_auth_secret()
                totp = pyotp.TOTP(secret)
                qr = qrcode.QRCode(version=1, box_size=10, border=5)
                qr.add_data(totp.provisioning_uri(name=user.username, issuer_name='Sourcing'))
                qr.make(fit=True)
               
                img = qr.make_image(fill_color="black", back_color="white")
                buffered = io.BytesIO()
                img.save(buffered, format="PNG")
                qr_code = base64.b64encode(buffered.getvalue()).decode()
               
                return render(request, 'connexion/login/google_auth_setup.html', {
                    'qr_code': qr_code,
                    'secret': secret
                })
    else:
        form = TwoFactorMethodForm()
   
    return render(request, 'connexion/login/two_factor_method.html', {'form': form})

def email_verification(request):
    if 'pre_2fa_user_id' not in request.session or '2fa_email_code' not in request.session:
        return redirect('login')
    
    user = Utilisateur.objects.get(id=request.session['pre_2fa_user_id'])
    
    if request.method == 'POST':
        form = EmailVerificationForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data['code']
            if code == request.session['2fa_email_code']:
                # Specify the backend explicitly
                login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                del request.session['pre_2fa_user_id']
                del request.session['2fa_email_code']
                user_name = user.get_full_name() or user.username
                messages.success(request, f'bienvenue {user_name} ! Vous êtes connecté.')
                # Redirect based on user type
                if user.type_user == 'AS':  # Agent Sourcing
                    return redirect('maps')
                elif user.type_user == 'FS':  # Fournisseur
                    return redirect('accueil_fournisseur')
                return redirect('maps')  # Default fallback
            else:
                messages.error(request, 'Code de vérification invalide')
    else:
        form = EmailVerificationForm()
    
    return render(request, 'emails/email_verification.html', {'form': form})

def google_auth_verification(request):
    if 'pre_2fa_user_id' not in request.session:
        return redirect('login')
    
    user = Utilisateur.objects.get(id=request.session['pre_2fa_user_id'])
    
    if request.method == 'POST':
        form = GoogleAuthVerificationForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data['code']
            if user.verify_google_auth_code(code):
                # Specify the backend explicitly
                login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                del request.session['pre_2fa_user_id']
                user_name = user.get_full_name() or user.username
                messages.success(request, f'bienvenue {user_name} ! Vous êtes connecté.')
                # Redirect based on user type
                if user.type_user == 'AS':  # Agent Sourcing
                    return redirect('maps')
                elif user.type_user == 'FS':  # Fournisseur
                    return redirect('accueil_fournisseur')
                return redirect('maps')  # Default fallback
            else:
                messages.error(request, 'Code d\'authentification invalide')
    else:
        form = GoogleAuthVerificationForm()
    
    return render(request, 'connexion/login/google_auth_verification.html', {'form': form})



from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.models import User
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)


def forgatpassword(request):
    """
    Vue pour gérer la demande de réinitialisation de mot de passe.
    Envoie un email à l'administrateur avec les informations de l'utilisateur.
    """
    
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        
        # Validation basique de l'email
        if not email:
            messages.error(request, "Veuillez entrer une adresse email.")
            return render(request, 'connexion/forgatpassword.html')
        
        # Vérification du format de l'email
        from django.core.validators import validate_email
        from django.core.exceptions import ValidationError
        
        try:
            validate_email(email)
        except ValidationError:
            messages.error(request, "Veuillez entrer une adresse email valide.")
            return render(request, 'connexion/forgatpassword.html')
        
        try:
            # Vérifier si un utilisateur actif avec cet email existe
            try:
                user = User.objects.get(email__iexact=email, is_active=True)
            except User.DoesNotExist:
                # Vérifier si l'email existe mais le compte est inactif
                if User.objects.filter(email__iexact=email, is_active=False).exists():
                    messages.warning(
                        request,
                        "Ce compte existe mais n'est pas activé. Veuillez contacter l'administrateur."
                    )
                else:
                    # Pour des raisons de sécurité, on ne révèle pas si l'email existe ou non
                    messages.info(
                        request, 
                        "Si cet email est associé à un compte, l'administrateur recevra votre demande."
                    )
                return render(request, 'connexion/forgatpassword.html')
            
            # Journalisation de la tentative
            logger.info(f"Tentative de réinitialisation pour l'email: {email}")
            
            # Vérifier si l'utilisateur a le droit de réinitialiser son mot de passe
            # (ajoutez ici des vérifications supplémentaires si nécessaire, comme des groupes spécifiques)
            if not user.has_usable_password():
                messages.warning(
                    request,
                    "Ce compte n'utilise pas de mot de passe pour se connecter. "
                    "Veuillez utiliser la méthode de connexion alternative."
                )
                return render(request, 'connexion/forgatpassword.html')
            
            # Email de l'administrateur (à configurer dans settings.py)
            admin_email = getattr(settings, 'ADMIN_EMAIL', 'ibrahimkabore025@gmail.com')
            
            # Contenu de l'email
            subject = f"Demande de réinitialisation de mot de passe - {user.username}"
            
            message = f"""
        Bonjour Administrateur,

        Un utilisateur a demandé la réinitialisation de son mot de passe.

        INFORMATIONS DE LA DEMANDE :
        ----------------------------
        - Nom d'utilisateur : {user.username}
        - Email : {user.email}
        - Nom complet : {user.get_full_name() or 'Non renseigné'}
        - Date de la demande : {timezone.now().strftime('%d/%m/%Y à %H:%M')}

        Merci de procéder à la réinitialisation du mot de passe pour cet utilisateur.

        ---
        Système Innov-Sourcing OOA
        Cet email a été généré automatiquement, merci de ne pas y répondre.
                    """
            
            # Envoi de l'email
            try:
                # Vérifier si l'email de l'administrateur est configuré
                if not admin_email:
                    logger.error("Aucun email d'administrateur configuré dans les paramètres")
                    raise ValueError("Configuration d'email manquante")
                
                # Envoyer l'email
                send_mail(
                    subject=subject,
                    message=message,
                    from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@innov-sourcing.com'),
                    recipient_list=[admin_email],
                    fail_silently=False,
                )
                
                # Log de succès avec plus d'informations
                logger.info(
                    f"Email de réinitialisation envoyé pour l'utilisateur: {user.username} "
                    f"à l'administrateur: {admin_email}"
                )
                
                # Message de succès plus informatif
                messages.success(
                    request, 
                    "✅ Votre demande a été envoyée avec succès !\n"
                    "📩 L'administrateur a été notifié et vous contactera sous 24-48h."
                )
                
                # Réinitialiser le formulaire après un envoi réussi
                return redirect('forgot_password')
                
            except Exception as e:
                # Log de l'erreur avec plus de détails
                error_msg = f"Erreur lors de l'envoi de l'email à {admin_email}: {str(e)}"
                logger.error(error_msg, exc_info=True)
                
                # Message d'erreur plus convivial
                messages.error(
                    request, 
                    "❌ Désolé, une erreur est survenue lors de l'envoi de votre demande.\n"
                    f"Veuillez contacter directement l'administrateur à l'adresse {admin_email}"
                )
                
                # En développement, on peut afficher plus de détails sur l'erreur
                if settings.DEBUG:
                    messages.info(request, f"Détails techniques: {str(e)}")
                
                # Ne pas révéler l'erreur technique à l'utilisateur en production
        
        except User.DoesNotExist:
            # Pour des raisons de sécurité, on affiche le même message
            messages.info(
                request, 
                "Si cet email est associé à un compte, l'administrateur recevra votre demande."
            )
        
        except Exception as e:
            # Log de l'erreur
            logger.error(f"Erreur inattendue dans forgatpassword: {str(e)}")
            
            messages.error(
                request, 
                "Une erreur inattendue s'est produite. Veuillez réessayer plus tard."
            )
    
    return render(request, 'connexion/forgatpassword.html')


# VERSION ALTERNATIVE AVEC SYSTÈME DE TOKENS (Plus sécurisé)
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.urls import reverse


def forgatpassword_with_token(request):
    """
    Version alternative avec système de tokens pour réinitialisation sécurisée.
    Cette version envoie un lien de réinitialisation directement à l'utilisateur.
    """
    
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        
        if not email:
            messages.error(request, "Veuillez entrer une adresse email.")
            return render(request, 'connexion/forgatpassword.html')
        
        try:
            user = User.objects.get(email=email)
            
            # Générer le token de réinitialisation
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            
            # Créer le lien de réinitialisation
            reset_link = request.build_absolute_uri(
                reverse('password_reset_confirm', kwargs={'uidb64': uid, 'token': token})
            )
            
            # Email à l'administrateur avec le lien
            admin_email = getattr(settings, 'ADMIN_EMAIL', 'admin@innov-sourcing.com')
            
            subject = f"Demande de réinitialisation - {user.username}"
            message = f"""
Bonjour Administrateur,

Demande de réinitialisation de mot de passe pour :
- Utilisateur : {user.username}
- Email : {user.email}
- Date : {timezone.now().strftime('%d/%m/%Y à %H:%M')}

Lien de réinitialisation à transmettre à l'utilisateur :
{reset_link}

Ce lien est valide pendant 24 heures.

---
Système Innov-Sourcing OOA
            """
            
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[admin_email],
                fail_silently=False,
            )
            
            messages.success(
                request,
                "Votre demande a été envoyée ! "
                "L'administrateur vous enverra un lien de réinitialisation."
            )
            
            logger.info(f"Token de réinitialisation généré pour: {user.username}")
            
        except User.DoesNotExist:
            messages.info(
                request,
                "Si cet email est associé à un compte, vous recevrez les instructions."
            )
        
        except Exception as e:
            logger.error(f"Erreur lors de la réinitialisation: {str(e)}")
            messages.error(
                request,
                "Une erreur s'est produite. Veuillez réessayer plus tard."
            )
    
    return render(request, 'connexion/forgatpassword.html')


# # FONCTION UTILITAIRE POUR L'ADMIN
# def admin_reset_user_password(user_id, new_password):
#     """
#     Fonction utilitaire pour que l'administrateur réinitialise un mot de passe.
#     Peut être appelée depuis l'interface admin Django.
#     """
#     try:
#         user = User.objects.get(id=user_id)
#         user.set_password(new_password)
#         user.save()
        
#         # Envoyer un email de confirmation à l'utilisateur
#         send_mail(
#             subject="Votre mot de passe a été réinitialisé",
#             message=f"""
# Bonjour {user.username},

# Votre mot de passe a été réinitialisé avec succès par l'administrateur.

# Vous pouvez maintenant vous connecter avec votre nouveau mot de passe.

# Si vous n'êtes pas à l'origine de cette demande, veuillez contacter immédiatement l'administrateur.

# ---
# Équipe Innov-Sourcing OOA
#             """,
#             from_email=settings.DEFAULT_FROM_EMAIL,
#             recipient_list=[user.email],
#             fail_silently=False,
#         )
        
#         logger.info(f"Mot de passe réinitialisé pour l'utilisateur: {user.username}")
#         return True
        
#     except User.DoesNotExist:
#         logger.error(f"Utilisateur avec l'ID {user_id} introuvable")
#         return False
#     except Exception as e:
#         logger.error(f"Erreur lors de la réinitialisation: {str(e)}")
#         return False
