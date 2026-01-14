from django.urls import path
from .views.accueil import AccueilView
from django.views.generic import RedirectView

app_name = 'website'
urlpatterns = [
    path('', RedirectView.as_view(pattern_name='website:accueil', permanent=False)),
    path('client/accueil/', AccueilView.as_view(), name='accueil'),
    path('client/accueil/<int:commodite_id>/', AccueilView.as_view(), name='accueil_avec_commodite'),
]