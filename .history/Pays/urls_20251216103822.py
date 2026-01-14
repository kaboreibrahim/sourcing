from django.urls import path
from .views import (
    PaysListView,
    PaysDetailView,
    PaysCreateView,
    PaysUpdateView,
    PaysDeleteView
)
from port.views import (
    PortListView,
    PortDetailView,
    PortCreateView,
    PortUpdateView,
    PortDeleteView,
    ZoneListAPI
)



urlpatterns = [
    # Pays
    path('pays/list/', PaysListView.as_view(), name='pays-list'),
    path('pays/create/', PaysCreateView.as_view(), name='pays-create'),
    path('pays/<uuid:pk>/', PaysDetailView.as_view(), name='pays-detail'),
    path('pays/<uuid:pk>/update/', PaysUpdateView.as_view(), name='pays-update'),
    path('pays/<uuid:pk>/delete/', PaysDeleteView.as_view(), name='pays-delete'),

    # Ports
    path('port/list/', PortListView.as_view(), name='port-list'),
    path('port/create/', PortCreateView.as_view(), name='port-create'),
    path('port/<uuid:pk>/', PortDetailView.as_view(), name='port-detail'),
    path('port/<uuid:pk>/update/', PortUpdateView.as_view(), name='port-update'),
    path('port/<uuid:pk>/delete/', PortDeleteView.as_view(), name='port-delete'),
    path('api/zones/', ZoneListAPI.as_view(), name='api_zones'),
    
]