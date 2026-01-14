from django.urls import path
from .views import list
 
urlpatterns = [
   path('list/', list, name='cotation_list'),
]
