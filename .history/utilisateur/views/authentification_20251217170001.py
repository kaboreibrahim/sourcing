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
    return redirect('login')

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
           
            if method == 'email':
                code = str(random.randint(100000, 999999))
                request.session['2fa_email_code'] = code
                
                # Préparer le contexte pour le template
                context = {
                    'code': code,
                    'user': user,
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
                if user.type_utilisateur == 'AS':  # Agent Sourcing
                    return redirect('maps')
                elif user.type_utilisateur == 'FS':  # Fournisseur
                    return redirect('accueil_fournisseur')
                return redirect('maps')  # Default fallback
            else:
                messages.error(request, 'Code d\'authentification invalide')
    else:
        form = GoogleAuthVerificationForm()
    
    return render(request, 'connexion/login/google_auth_verification.html', {'form': form})