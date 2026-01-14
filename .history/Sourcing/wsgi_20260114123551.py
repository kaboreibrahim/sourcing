"""
WSGI config for Sourcing project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

import os
from django.core.wsgi import get_wsgi_application
from whitenoise import WhiteNoise

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Sourcing.settings")

# This application object is used by the development server
# as well as any WSGI server configured to use this file.
application = get_wsgi_application()

# Wrap the Django application with WhiteNoise
application = WhiteNoise(
    application,
    root=os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static'),
    prefix='static/'
)
