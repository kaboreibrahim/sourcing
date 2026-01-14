from django.urls import path
from .views import (
    FournisseurListView, FournisseurDetailView, FournisseurCreateView,
    FournisseurUpdateView, FournisseurDeleteView,
    FournisseurMapView, FournisseurStatsView, FournisseurSearchView,
    FournisseurExportView, LoadLocalitesView,
    PortFournisseurCreateView,PortFournissuerListView,
    FournisseurZoneListAPI,FournisseurVilleListAPI
)

urlpatterns = [
    # URLs pour les Fournisseurs
    path('fournisseurs/', FournisseurListView.as_view(), name='fournisseur-list'),
    path('fournisseurs/create/', FournisseurCreateView.as_view(), name='fournisseur-create'),
    path('ajax/load-localites/', LoadLocalitesView.as_view(), name='ajax_load_localites'),
    path('fournisseurs/search/', FournisseurSearchView.as_view(), name='fournisseur-search'),
    path('fournisseurs/map/', FournisseurMapView.as_view(), name='fournisseur-map'),
    path('fournisseurs/stats/', FournisseurStatsView.as_view(), name='fournisseur-stats'),
    path('fournisseurs/<uuid:pk>/', FournisseurDetailView.as_view(), name='fournisseur-detail'),
    path('fournisseurs/<uuid:pk>/update/', FournisseurUpdateView.as_view(), name='fournisseur-update'),
    path('fournisseurs/<uuid:pk>/delete/', FournisseurDeleteView.as_view(), name='fournisseur-delete'),
    path('fournisseurs/export/', FournisseurExportView.as_view(), name='fournisseur-export'),

    path('fournisseurs/ports/add/',PortFournisseurCreateView.as_view(),name='fournisseur-port-add'),
    path('fournisseurs/laisons/',PortFournissuerListView.as_view(),name='port-fournisseur-list'),

    path('fournisseurs/api/zones/', FournisseurZoneListAPI.as_view(), name='fournisseur_api_zones'),
    path('fournisseurs/api/villes/', FournisseurVilleListAPI.as_view(), name='fournisseur_api_villes'),


    
]