from django.urls import path
from .views import VilleListView, VilleCreateView, VilleDetailView, VilleUpdateView, VilleDeleteView
from .views import LocaliteListView, localiteCreateView, LocaliteDeleteView
urlpatterns = [
   # URLs pour les Villes
    path('villes/', VilleListView.as_view(), name='ville-list'),
    path('villes/create/', VilleCreateView.as_view(), name='ville-create'),
    path('villes/<uuid:pk>/', VilleDetailView.as_view(), name='ville-detail'),
    path('villes/<uuid:pk>/update/', VilleUpdateView.as_view(), name='ville-update'),
    path('villes/<uuid:pk>/delete/', VilleDeleteView.as_view(), name='ville-delete'),

    # URLs pour les Localites
    path('localites/', LocaliteListView.as_view(), name='localite-list'),
    path('localites/create/', localiteCreateView.as_view(), name='localite-create'),
    path('localites/<uuid:pk>/delete/', LocaliteDeleteView.as_view(), name='localite-delete'),
    
]
