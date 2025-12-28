"""
Local Development Settings
"""
from .base import *

DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0', '*']

# Development database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': get_env('DB_NAME', 'calculus_db'),
        'USER': get_env('DB_USER', 'calculus_user'),
        'PASSWORD': get_env('DB_PASSWORD', 'calculus_password123'),
        'HOST': get_env('DB_HOST', 'localhost'),
        'PORT': get_env('DB_PORT', '5433'),
    },
}

# Development logging
LOGGING['root']['level'] = 'DEBUG'
LOGGING['loggers']['django']['level'] = 'DEBUG'

# Reduce autoreload verbosity
LOGGING['loggers']['django.utils.autoreload'] = {
    'handlers': ['console', 'file'],
    'level': 'INFO',  # Change from DEBUG to INFO to reduce file monitoring logs
    'propagate': False,
}

# CORS settings for development
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True
