"""
Settings package - 根據環境變數選擇配置
"""
import os

environment = os.environ.get('DJANGO_ENV', 'local')

if environment == 'production':
    from .production import *
elif environment == 'test':
    from .base import *
    DEBUG = True
    DATABASES['default']['NAME'] = 'test_' + DATABASES['default']['NAME']
else:
    from .local import *
