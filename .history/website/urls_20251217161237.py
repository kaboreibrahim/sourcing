from django.urls import path
from .views.accueil import AccueilView
from django.views.generic import RedirectView
urlpatterns = [
    path('',RedirectView.as_view(url='/accueil/')),
    path('accueil/', AccueilView.as_view(), name='accueil'),
]