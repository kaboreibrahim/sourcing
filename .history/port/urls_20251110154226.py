# port/urls.py
from django.urls import path
from .views import get_ports_by_pays

urlpatterns = [
    # ... autres URLs
    path('api/ports-by-pays/<int:pays_id>/', get_ports_by_pays, name='ports-by-pays'),
]