from django.urls import path
from . import views


urlpatterns = [
    # URLs avec vues basées sur des classes (CBV)
    path('creer/', views.DemandeCotationCreateView.as_view(), name='cotation_create'),
    path('liste/', views.DemandeCotationListView.as_view(), name='cotation_list'),
    path('detail/<uuid:demande_id>/', views.detail_demande_cotation, name='cotation_detail'),
    path('modifier/<uuid:pk>/', views.DemandeCotationUpdateView.as_view(), name='cotation_update'),
    path('success/', views.cotation_success_view, name='cotation_success'),
    path('emails/', views.EmailQueueListView.as_view(), name='email_queue_list')
    
    
]
