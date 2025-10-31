from django.urls import path
from villes.views.ville import VilleListView, VilleCreateView, VilleDetailView, VilleUpdateView, VilleDeleteView

urlpatterns = [
   # URLs pour les Villes
    path('villes/', VilleListView.as_view(), name='ville-list'),
    path('villes/create/', VilleCreateView.as_view(), name='ville-create'),
    path('villes/<uuid:pk>/', VilleDetailView.as_view(), name='ville-detail'),
    path('villes/<uuid:pk>/update/', VilleUpdateView.as_view(), name='ville-update'),
    path('villes/<uuid:pk>/delete/', VilleDeleteView.as_view(), name='ville-delete'),
     
]
