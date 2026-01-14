from django.urls import path
from .views.accueil import AccueilView

urlpatterns = [
    path('', AccueilView.as_view(), name='accueil'),
]