from django.urls import path
from .views.accueil import AccueilView
from django.views.generic import RedirectView

app_name = 'website'
urlpatterns = [
    path('',RedirectView.as_view(url='/client/accueil/')),
    path('client/accueil/', AccueilView.as_view(), name='accueil'),
]