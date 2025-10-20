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
 
from uuid import UUID
import random
from django.core.mail import send_mail
import pyotp
import qrcode
import io
import base64
