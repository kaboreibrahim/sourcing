from django.urls import path
from .views import  ville.VilleListView, ville.VilleCreateView, ville.VilleDetailView, ville.VilleUpdateView, ville.VilleDeleteView

urlpatterns = [
   # URLs pour les Villes
    path('villes/', ville.VilleListView.as_view(), name='ville-list'),
    path('villes/create/', ville.VilleCreateView.as_view(), name='ville-create'),
    path('villes/<uuid:pk>/', ville.VilleDetailView.as_view(), name='ville-detail'),
    path('villes/<uuid:pk>/update/', ville.VilleUpdateView.as_view(), name='ville-update'),
    path('villes/<uuid:pk>/delete/', ville.VilleDeleteView.as_view(), name='ville-delete'),
     
]
