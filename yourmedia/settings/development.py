"""
Development settings for yourmedia project.
"""

from .base import *

# Debug mode ON for development
DEBUG = True

# Allow all hosts in development
ALLOWED_HOSTS = ['*']

# Database - use localhost in development
DATABASES['default']['HOST'] = 'localhost'

# Email backend (console for development)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Django Debug Toolbar (optional, add to INSTALLED_APPS if needed)
# INSTALLED_APPS += ['debug_toolbar']
# MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']
# INTERNAL_IPS = ['127.0.0.1']

# Logging - more verbose in development
LOGGING['root']['level'] = 'DEBUG'
LOGGING['loggers']['apps']['level'] = 'DEBUG'
