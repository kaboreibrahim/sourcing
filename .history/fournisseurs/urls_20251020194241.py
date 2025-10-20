from django.urls import path
from . import views

app_name = 'fournisseurs'

urlpatterns = [
    # URLs pour les Fournisseurs
    path('list/', views.FournisseurListView.as_view(), name='fournisseur'),
    path('create/', views.FournisseurCreateView.as_view(), name='fournisseur-create'),
    path('<uuid:pk>/', views.FournisseurDetailView.as_view(), name='fournisseur-detail'),
    path('<uuid:pk>/update/', views.FournisseurUpdateView.as_view(), name='fournisseur-update'),
    path('<uuid:pk>/delete/', views.FournisseurDeleteView.as_view(), name='fournisseur-delete'),
]
