from django.urls import path
from . import views

app_name = 'fournisseurs'

urlpatterns = [
    # URLs pour les Fournisseurs
    path('fournisseurs/', views.FournisseurListView.as_view(), name='fournisseur-list'),
    path('fournisseurs/create/', views.FournisseurCreateView.as_view(), name='fournisseur-create'),
    path('fournisseurs/<uuid:pk>/', views.FournisseurDetailView.as_view(), name='fournisseur-detail'),
    path('fournisseurs/<uuid:pk>/update/', views.FournisseurUpdateView.as_view(), name='fournisseur-update'),
    path('fournisseurs/<uuid:pk>/delete/', views.FournisseurDeleteView.as_view(), name='fournisseur-delete'),
]
