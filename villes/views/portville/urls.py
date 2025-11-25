from django.urls import path
from .create import VillePortCreateView, LoadPortsByPaysView
from .detail import VillePortDetailView

app_name = 'portville'

urlpatterns = [
    path('create/', VillePortCreateView.as_view(), name='create'),
    path('load-ports/', LoadPortsByPaysView.as_view(), name='load-ports'),
    path('<uuid:pk>/', VillePortDetailView.as_view(), name='detail'),
]
