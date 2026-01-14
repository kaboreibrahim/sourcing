"""
URL configuration for Sourcing project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from utilisateur.views import error
from django.conf.urls import handler404, handler403, handler500, handler400
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
urlpatterns = [
    path("admin/", admin.site.urls),

    ######url de l'application zones
    path('zones/', include('zones.urls')),
    
    ######url de l'application villes
    path('villes/', include('villes.urls')),
    
    ######url de l'application pays
    path('Pays/', include('Pays.urls')),
    
    ######url de l'application fournisseurs
    path('fournisseurs/', include('fournisseurs.urls')),
    
    ######url de l'application commodites
    path('commodites/', include('commodites.urls')),

    ######### url du site web######""
    path ('',include('website.urls')),
    
    ######url de l'application utilisateurs
    path('utilisateur/', include('utilisateur.urls')),

     ######url de l'application cotation
    path('cotation/', include('cotation.urls')),
]

# Servir les fichiers statiques et médias en mode développement
if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

    ######url de l'application echantillonnages
    path('echantillonnages/', include('echantillonnages.urls')),
]

handler404 = error.custom_page_not_found
handler403 = error.custom_permission_denied
handler500 = error.custom_server_error
handler400 = error.custom_bad_request
