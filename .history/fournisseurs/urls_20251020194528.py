from django.urls import path
from .views import (
    FournisseurListView, FournisseurCreateView, 
    FournisseurDetailView, FournisseurUpdateView, 
    FournisseurDeleteView
)

app_name = 'fournisseurs'

urlpatterns = [
    # URLs pour les Fournisseurs
    path('fournisseurs/', FournisseurListView.as_view(), name='fournisseur-list'),
    path('fournisseurs/create/', FournisseurCreateView.as_view(), name='fournisseur-create'),
    path('fournisseurs/<uuid:pk>/', FournisseurDetailView.as_view(), name='fournisseur-detail'),
    path('fournisseurs/<uuid:pk>/update/', FournisseurUpdateView.as_view(), name='fournisseur-update'),
    path('fournisseurs/<uuid:pk>/delete/', FournisseurDeleteView.as_view(), name='fournisseur-delete'),
]
