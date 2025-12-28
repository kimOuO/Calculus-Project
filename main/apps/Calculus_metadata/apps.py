"""
Calculus_metadata App Config
"""
from django.apps import AppConfig


class CalculusMetadataConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'main.apps.Calculus_metadata'
    verbose_name = 'Calculus Metadata'
    
    def ready(self):
        """App initialization"""
        pass
