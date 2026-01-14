from django.urls import path
from .views import AccueilFournisseurView, DetailCommoditeFournisseurView

urlpatterns = [
  ############ INDEX FOURNISSEUR ############

    path('accueil/fournisseurs/',AccueilFournisseurView.as_view(), name='accueil_fournisseur'),
    path('fournisseurs/commodite/<uuid:pk>/', DetailCommoditeFournisseurView.as_view(), name='detail_commodite'),
 
     
]
