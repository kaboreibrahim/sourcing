from django.urls import path
from .views import (
    PaysListView,
    PaysDetailView,
    PaysCreateView,
    PaysUpdateView,
    PaysDeleteView
)

app_name = 'pays'

urlpatterns = [
    path('', PaysListView.as_view(), name='list'),
    path('nouveau/', PaysCreateView.as_view(), name='create'),
    path('<uuid:pk>/', PaysDetailView.as_view(), name='detail'),
    path('<uuid:pk>/modifier/', PaysUpdateView.as_view(), name='update'),
    path('<uuid:pk>/supprimer/', PaysDeleteView.as_view(), name='delete'),
]