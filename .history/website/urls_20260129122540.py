from django.urls import path
from .views.accueil import AccueilView , robots_txt 
from django.views.generic import RedirectView,TemplateView

app_name = 'website'
urlpatterns = [
    path('',RedirectView.as_view(url='/client/accueil/')),
    path('client/accueil/', AccueilView.as_view(), name='accueil'),
    path('robots.txt', robots_txt, name='robots_txt'),
    path(r'^set_language/$', set_language, name='set_language'),
    path('sitemap.xml', TemplateView.as_view(template_name='sitemap.xml', content_type='application/xml')),
]