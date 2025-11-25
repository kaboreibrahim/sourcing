from django.urls import path, include
from .views import (localiteCreateView, LocaliteListView, LocaliteDeleteView, LocaliteUpdateView, LocaliteDetailView,
VilleListView, VilleCreateView, VilleDetailView, VilleUpdateView, VilleDeleteView,
VillePortListView, VillePortCreateView, LoadPortsByPaysView,
PortLocaliteListView, LoadPortsByPaysLocaliteView,PortLocaliteCreateView,PortLocaliteDetailView
)

# Import des vues de portville
from .views.portville.detail import VillePortDetailView

urlpatterns = [
   # URLs pour les Villes
    path('villes/', VilleListView.as_view(), name='ville-list'),
    path('villes/create/', VilleCreateView.as_view(), name='ville-create'),
    path('villes/<uuid:pk>/', VilleDetailView.as_view(), name='ville-detail'),
    path('villes/<uuid:pk>/update/', VilleUpdateView.as_view(), name='ville-update'),
    path('villes/<uuid:pk>/delete/', VilleDeleteView.as_view(), name='ville-delete'),

    # URLs pour les Localites
    path('localites/', LocaliteListView.as_view(), name='localite-list'),
    path('localites/<uuid:pk>/delete/', LocaliteDeleteView.as_view(), name='localite-delete'),
    path('localites/create/', localiteCreateView.as_view(), name='localite-create'),
    path('localites/<uuid:pk>/update/', LocaliteUpdateView.as_view(), name='localite-update'),
    path('localites/<uuid:pk>/', LocaliteDetailView.as_view(), name='localite-detail'),

    # URLs pour les Port-Ville
    path('port-ville/', VillePortListView.as_view(), name='ville-port-list'),
    path('port-ville/create/', VillePortCreateView.as_view(), name='ville-port-create'),
    path('port-ville/<uuid:pk>/', VillePortDetailView.as_view(), name='ville-port-detail'),
    path('portville/load-ports/', LoadPortsByPaysView.as_view(), name='load-ports-by-pays'),

    # URLs pour les Port-Localite
    path('port-localite/', PortLocaliteListView.as_view(), name='port-localite-list'),
    path('port-localite/create/', PortLocaliteCreateView.as_view(), name='port-localite-create'),
    path('port-localite/<uuid:pk>/', PortLocaliteDetailView.as_view(), name='port-localite-detail'),
    path('portville/load-ports/', LoadPortsByPaysLocaliteView.as_view(), name='load-ports-by-pays-localite'),
  
 
    
    
]
