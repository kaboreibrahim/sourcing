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
from utilisateur.forms import LoginForm
from uuid import UUID
import random
from django.core.mail import send_mail
import pyotp
import qrcode
import io
import base64
 

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
    return render(request, 'registration/login.html', {'form': form})