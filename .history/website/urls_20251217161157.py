from django.urls import path
from .views.accueil import AccueilView

urlpatterns = [
    path('accueil/', AccueilView.as_view(), name='accueil'),
]