"""
Base Django settings for yourmedia project.
This file contains settings common to all environments.
"""

import os
from pathlib import Path
from datetime import timedelta
from decouple import config

# Build paths inside the project
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Security
SECRET_KEY = config('DJANGO_SECRET_KEY', default='dev-secret-key-change-in-production')
DEBUG = config('DJANGO_DEBUG', default=True, cast=bool)
ALLOWED_HOSTS = config('DJANGO_ALLOWED_HOSTS', default='localhost,127.0.0.1').split(',')

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.postgres',  # PostgreSQL specific features

    # Third-party apps
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'django_filters',
    'drf_spectacular',

    # Local apps
    'apps.accounts',
    'apps.media_catalog',
    'apps.collections',
    'apps.data_sync',
    'apps.social',
    'apps.recommendations',
    'core',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Serve static files
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'yourmedia.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'yourmedia.wsgi.application'

# Database - PostgreSQL
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('POSTGRES_DB', default='yourmedia_db'),
        'USER': config('POSTGRES_USER', default='yourmedia_user'),
        'PASSWORD': config('POSTGRES_PASSWORD', default='changeme'),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='5432'),
    }
}

# Neo4j Configuration
NEO4J_CONFIG = {
    'URI': config('NEO4J_URI', default='bolt://localhost:7687'),
    'USER': config('NEO4J_USER', default='neo4j'),
    'PASSWORD': config('NEO4J_PASSWORD', default='changeme'),
}

# Redis Configuration
REDIS_URL = config('REDIS_URL', default='redis://localhost:6379/0')

# Custom User Model
AUTH_USER_MODEL = 'accounts.User'

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 8,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Media files (User uploads)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# REST Framework Configuration
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ),
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

# JWT Configuration
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(
        minutes=config('JWT_ACCESS_TOKEN_LIFETIME_MINUTES', default=60, cast=int)
    ),
    'REFRESH_TOKEN_LIFETIME': timedelta(
        days=config('JWT_REFRESH_TOKEN_LIFETIME_DAYS', default=7, cast=int)
    ),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'AUTH_HEADER_TYPES': ('Bearer',),
}

# CORS Configuration
CORS_ALLOWED_ORIGINS = config(
    'CORS_ALLOWED_ORIGINS',
    default='http://localhost:3000,http://127.0.0.1:3000'
).split(',')
CORS_ALLOW_CREDENTIALS = True

# API Documentation (drf-spectacular)
SPECTACULAR_SETTINGS = {
    'TITLE': 'Your Media Collection API',
    'DESCRIPTION': 'API for managing personal media collections',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
}

# Celery Configuration
CELERY_BROKER_URL = config('CELERY_BROKER_URL', default='redis://localhost:6379/0')
CELERY_RESULT_BACKEND = config('CELERY_RESULT_BACKEND', default='redis://localhost:6379/0')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE

# External API Configuration
TMDB_API_KEY = config('TMDB_API_KEY', default='')
TMDB_API_BASE_URL = config('TMDB_API_BASE_URL', default='https://api.themoviedb.org/3')

# Logging Configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'django.log',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'apps': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}
