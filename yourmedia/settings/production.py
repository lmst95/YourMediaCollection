"""
Production settings for yourmedia project.
"""

from .base import *

# Security settings for production
DEBUG = False

# Security enhancements
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Database - use Docker service names in production
DATABASES['default']['HOST'] = config('DB_HOST', default='postgres')

# Email backend (configure with real SMTP in production)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = True
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')

# Logging - less verbose in production
LOGGING['root']['level'] = 'WARNING'
LOGGING['loggers']['apps']['level'] = 'INFO'
