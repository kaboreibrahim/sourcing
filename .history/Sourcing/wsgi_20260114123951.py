"""
WSGI config for Sourcing project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Sourcing.settings")

application = get_wsgi_application()

# Ajout de WhiteNoise pour servir les fichiers statiques en production
from whitenoise import WhiteNoise
from django.conf import settings

if not settings.DEBUG:
    application = WhiteNoise(application, root=settings.STATIC_ROOT)
    application.add_files(settings.STATIC_ROOT, prefix=settings.STATIC_URL)
    application.add_files(settings.MEDIA_ROOT, prefix=settings.MEDIA_URL)
