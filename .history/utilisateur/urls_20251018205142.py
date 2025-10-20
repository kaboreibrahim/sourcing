from django.urls import path
from django.views.generic import RedirectView
from utilisateur.views import connexion,two_factor_method,email_verification,google_auth_verification
urlpatterns = [

    ########### AUTHENTIFICATION ###########
    path('',RedirectView.as_view(url='/login/')),
    path('login/', connexion, name='login'),
    path('two-factor-method/', two_factor_method, name='two_factor_method'),
    path('email-verification/', email_verification, name='email_verification'),
    path('google-auth-verification/', google_auth_verification, name='google_auth_verification'),
 ]
