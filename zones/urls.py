from django.urls import path
from .views import ZoneListView, ZoneCreateView, ZoneDetailView, ZoneUpdateView, ZoneDeleteView
from .api import zones_by_pays

urlpatterns = [
    # URLs pour les Zones
    path('zones/', ZoneListView.as_view(), name='zone-list'),
    path('zones/create/', ZoneCreateView.as_view(), name='zone-create'),
    path('zones/<uuid:pk>/', ZoneDetailView.as_view(), name='zone-detail'),
    path('zones/<uuid:pk>/update/', ZoneUpdateView.as_view(), name='zone-update'),
    path('zones/<uuid:pk>/delete/', ZoneDeleteView.as_view(), name='zone-delete'),
    
    # API Endpoints
    path('api/zones/by-pays/<uuid:pays_id>/', zones_by_pays, name='api-zones-by-pays'),
]
