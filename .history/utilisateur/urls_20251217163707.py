from django.urls import path
from django.views.generic import RedirectView
from utilisateur.views import (connexion,two_factor_method,email_verification
                                ,google_auth_verification,fournisseurs_map,user_logout)
from utilisateur.views import FournisseursAPIView
from  django.conf.urls import handler404
urlpatterns = [

    ########### AUTHENTIFICATION ###########
    path('login/', connexion, name='login'),
    path('two-factor-method/', two_factor_method, name='two_factor_method'),
    path('email-verification/', email_verification, name='email_verification'),
    path('google-auth-verification/', google_auth_verification, name='google_auth_verification'),
    path('logout/', user_logout, name='logout'),

    ########### INDEX  ###########
    path('accueil/map/',fournisseurs_map, name='maps'),
    path('api/fournisseurs/', FournisseursAPIView.as_view(), name='api_fournisseurs'),

    ############ INDEX FOURNISSEUR ############

    path('accuel/fournisseurs/',)
 ]

