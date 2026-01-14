from django.urls import path
from . import views

app_name = 'cotation'
urlpatterns = [
    # URLs avec vues basées sur des classes (CBV)
    #path('creer/', views.DemandeCotationCreateView.as_view(), name='cotation_create'),
    path('liste/', views.DemandeCotationListView.as_view(), name='cotation_list'),
    # path('detail/<int:pk>/', views.DemandeCotationDetailView.as_view(), name='cotation_detail'),
    # path('modifier/<int:pk>/', views.DemandeCotationUpdateView.as_view(), name='cotation_update'),
    # path('success/', views.cotation_success_view, name='cotation_success'),
    
    # URLs alternatives avec vues basées sur des fonctions (FBV)
    # Décommentez ces lignes si vous préférez utiliser les vues fonctions
    # path('creer/', views.create_demande_cotation, name='cotation_create'),
    # path('liste/', views.list_demandes_cotation, name='cotation_list'),
    # path('detail/<int:pk>/', views.detail_demande_cotation, name='cotation_detail'),
]
