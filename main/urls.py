"""
Main URLs Configuration
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v0.1/Calculus_oom/Calculus_metadata/', include('main.apps.Calculus_metadata.api.urls')),
]
