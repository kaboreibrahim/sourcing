from django.urls import path
from .views import (
    FournisseurListView, FournisseurDetailView, FournisseurCreateView,
    FournisseurUpdateView, FournisseurDeleteView,
    FournisseurMapView, FournisseurStatsView, FournisseurSearchView
)

urlpatterns = [
    # URLs pour les Fournisseurs
    path('fournisseurs/', FournisseurListView.as_view(), name='fournisseur-list'),
    path('fournisseurs/create/', FournisseurCreateView.as_view(), name='fournisseur-create'),
    path('fournisseurs/search/', FournisseurSearchView.as_view(), name='fournisseur-search'),
    path('fournisseurs/map/', FournisseurMapView.as_view(), name='fournisseur-map'),
    path('fournisseurs/stats/', FournisseurStatsView.as_view(), name='fournisseur-stats'),
    path('fournisseurs/<uuid:pk>/', FournisseurDetailView.as_view(), name='fournisseur-detail'),
    path('fournisseurs/<uuid:pk>/update/', FournisseurUpdateView.as_view(), name='fournisseur-update'),
    path('fournisseurs/<uuid:pk>/delete/', FournisseurDeleteView.as_view(), name='fournisseur-delete'),
]