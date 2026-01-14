from django.urls import path
from .views import AccueilFournisseurView, DetailCommoditeFournisseurView,AjouterEchantillonView,ModifierEchantillonView

urlpatterns = [
  ############ INDEX FOURNISSEUR ############

    path('accueil/fournisseurs/',AccueilFournisseurView.as_view(), name='accueil_fournisseur'),
    path('fournisseurs/commodite/<uuid:pk>/', DetailCommoditeFournisseurView.as_view(), name='detail_commodite'),
    path('ajouter/<uuid:commodite_id>/', AjouterEchantillonView.as_view(), name='ajouter'),
    path(
        'echantillonnages/echantillons/<uuid:pk>/modifier/',
        ModifierEchantillonView.as_view(),
        name='modifier_echantillon'
    ),
    
     
]
