from django.urls import path
from .views import (
    CommoditeListView, CommoditeDetailView, CommoditeCreateView, 
    CommoditeUpdateView, CommoditeDeleteView,
    FournisseurCommoditeListView, FournisseurCommoditeCreateView, 
    FournisseurCommoditeDeleteView,
    CommoditeStatsView
)

urlpatterns = [
    # URLs pour les Commodités
    path('commodites/', CommoditeListView.as_view(), name='commodite-list'),
    path('commodites/create/', CommoditeCreateView.as_view(), name='commodite-create'),
    path('commodites/stats/', CommoditeStatsView.as_view(), name='commodite-stats'),
    path('commodites/<uuid:pk>/', CommoditeDetailView.as_view(), name='commodite-detail'),
    path('commodites/<uuid:pk>/update/', CommoditeUpdateView.as_view(), name='commodite-update'),
    path('commodites/<uuid:pk>/delete/', CommoditeDeleteView.as_view(), name='commodite-delete'),
    
    # URLs pour les Liaisons Fournisseur-Commodité
    path('liaisons/', FournisseurCommoditeListView.as_view(), name='liaison-list'),
    path('liaisons/create/', FournisseurCommoditeCreateView.as_view(), name='liaison-create'),
    path('liaisons/<uuid:pk>/delete/', FournisseurCommoditeDeleteView.as_view(), name='liaison-delete'),
]